import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='urllib3')

import pickle
import os
import requests
import argparse
import humanize
import yaml
import dateparser
import hashlib
from datetime import datetime
from dateutil.parser import isoparse, ParserError
from discord_notifier import send_discord_message, format_governance_for_discord, format_status_for_discord
from slack_notifier import send_slack_message, format_governance_for_slack, format_status_for_slack
from telegram_notifier import send_telegram_message_sync, format_governance_for_telegram, format_status_for_telegram
from statuspage_notifier import update_statuspage, format_status_for_statuspage
from loguru import logger
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

PICKLE_FILE = 'sent_updates.pkl'
COMPONENTS_FILE = 'affected_components.pkl'
CONFIG_FILE = 'config.yaml'

def load_config():
    with open(CONFIG_FILE, 'r') as file:
        config = yaml.safe_load(file)
    return config

def get_config_mtime():
    return os.path.getmtime(CONFIG_FILE)

def load_affected_components():
    if os.path.exists(COMPONENTS_FILE):
        with open(COMPONENTS_FILE, 'rb') as f:
            logger.info("Loaded affected components from pickle file")
            return pickle.load(f)
    logger.info("No affected components found, returning empty dict")
    return {}

def save_affected_components(affected_components):
    with open(COMPONENTS_FILE, 'wb') as f:
        pickle.dump(affected_components, f)
    logger.info("Saved affected components to pickle file")

config = load_config()
config_mtime = get_config_mtime()
avatar_url = config['avatar_url']
statuspages = config['statuspages']
customers = config['customers']
affected_components = load_affected_components()

def parse_date(date_str, incident_or_proposal_id, date_type):
    logger.debug(f"Raw {date_type} date for ID {incident_or_proposal_id}: {date_str}")
    try:
        logger.debug(f"Attempting ISO 8601 parse for {date_type} date: {date_str}")
        return isoparse(date_str)
    except (ParserError, ValueError):
        logger.debug(f"Attempting relative time parse for {date_type} date: {date_str}")
        parsed_date = dateparser.parse(date_str)
        if parsed_date:
            return parsed_date
        else:
            logger.error(f"Failed to parse {date_type} date for ID {incident_or_proposal_id}: {date_str}")
            return date_str

def hash_data(data):
    data_copy = data.copy()
    # Remove _display fields
    for key in list(data_copy.keys()):
        if key.endswith('_display'):
            del data_copy[key]
    data_str = str(data_copy)
    logger.debug(f"Hashing data: {data_str}")
    return hashlib.md5(data_str.encode('utf-8')).hexdigest()

def load_sent_updates():
    if os.path.exists(PICKLE_FILE):
        with open(PICKLE_FILE, 'rb') as f:
            logger.info("Loaded sent updates from pickle file")
            return pickle.load(f)
    logger.info("No sent updates found, returning empty set")
    return set()

def save_sent_updates(sent_updates):
    with open(PICKLE_FILE, 'wb') as f:
        pickle.dump(sent_updates, f)
    logger.info("Saved sent updates to pickle file")

def fetch_status_updates(api_key, page_id):
    url = f"https://api.statuspage.io/v1/pages/{page_id}/incidents"
    headers = {"Authorization": f"OAuth {api_key}"}
    
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504, 522, 524])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    
    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()
        logger.info("Fetched status updates")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch status updates: {e}")
        return []

def fetch_statuspage_components(api_key, page_id):
    url = f"https://api.statuspage.io/v1/pages/{page_id}/components"
    headers = {"Authorization": f"OAuth {api_key}"}
    
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504, 522, 524])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    
    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()
        logger.info(f"Fetched components for status page {page_id}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch components for status page {page_id}: {e}")
        return []

def format_status_update(incident):
    latest_update = incident["incident_updates"][0] if incident["incident_updates"] else {}
    created_at = incident["created_at"]
    updated_at = incident["updated_at"]
    resolved_at = incident.get("resolved_at")

    created_at_display = humanize.naturaltime(parse_date(created_at, incident["id"], "created_at"))
    updated_at_display = humanize.naturaltime(parse_date(updated_at, incident["id"], "updated_at"))
    resolved_at_display = humanize.naturaltime(parse_date(resolved_at, incident["id"], "resolved_at")) if resolved_at else None

    formatted_update = {
        "id": incident["id"],
        "title": incident["name"],
        "link": incident["shortlink"],
        "status": incident["status"],
        "created_at": created_at,
        "created_at_display": created_at_display,
        "updated_at": updated_at,
        "updated_at_display": updated_at_display,
        "resolved_at": resolved_at,
        "resolved_at_display": resolved_at_display,
        "impact": incident["impact"],
        "latest_update": latest_update.get('body', 'No updates available.')
    }
    return formatted_update

def fetch_governance_proposals():
    url = 'https://zetachain.blockpi.network/lcd/v1/public/cosmos/gov/v1/proposals?proposal_status=PROPOSAL_STATUS_UNSPECIFIED&pagination.count_total=true&pagination.reverse=true'
    headers = {'accept': 'application/json'}
    
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504, 522, 524])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    
    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()
        logger.info("Fetched governance proposals")
        return response.json().get('proposals', [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch governance proposals: {e}")
        return []

def format_governance_proposal(proposal):
    proposal_link = f"https://hub.zetachain.com/governance/proposal/{proposal['id']}"
    status_icon = {
        "PROPOSAL_STATUS_REJECTED": ":x:",
        "PROPOSAL_STATUS_PASSED": ":white_check_mark:",
        "PROPOSAL_STATUS_UNSPECIFIED": ":grey_question:"
    }.get(proposal["status"], ":grey_question:")
    
    final_tally_result = proposal.get("final_tally_result", {})
    yes_count = int(final_tally_result.get("yes_count", "0")) / 1e6
    abstain_count = int(final_tally_result.get("abstain_count", "0")) / 1e6
    no_count = int(final_tally_result.get("no_count", "0")) / 1e6
    no_with_veto_count = int(final_tally_result.get("no_with_veto_count", "0")) / 1e6
    total_votes = yes_count + abstain_count + no_count + no_with_veto_count

    yes_percentage = (yes_count / total_votes) * 100 if total_votes > 0 else 0
    abstain_percentage = (abstain_count / total_votes) * 100 if total_votes > 0 else 0
    no_percentage = (no_count / total_votes) * 100 if total_votes > 0 else 0
    no_with_veto_percentage = (no_with_veto_count / total_votes) * 100 if total_votes > 0 else 0

    submit_time = humanize.naturaltime(parse_date(proposal['submit_time'], proposal['id'], "submit_time"))
    deposit_end_time = humanize.naturaltime(parse_date(proposal['deposit_end_time'], proposal['id'], "deposit_end_time"))
    voting_end_time = humanize.naturaltime(parse_date(proposal['voting_end_time'], proposal['id'], "voting_end_time"))

    formatted_proposal = {
        "status_icon": status_icon,
        "id": proposal['id'],
        "title": proposal['title'],
        "summary": proposal['summary'],
        "status": proposal['status'],
        "type": proposal['messages'][0]['@type'],
        "submit_time": submit_time,
        "deposit_end_time": deposit_end_time,
        "voting_end_time": voting_end_time,
        "yes_count": yes_count,
        "abstain_count": abstain_count,
        "no_count": no_count,
        "no_with_veto_count": no_with_veto_count,
        "yes_percentage": yes_percentage,
        "abstain_percentage": abstain_percentage,
        "no_percentage": no_percentage,
        "no_with_veto_percentage": no_with_veto_percentage,
        "proposal_link": proposal_link
    }
    return formatted_proposal

def match_customers_to_incident(api_key, page_id, incident, affected_components):
    components = fetch_statuspage_components(api_key, page_id)
    logger.debug(f"Components: {components}")
    
    affected_customers = []
    incident_components = set(component["name"] for component in components if component["status"] != "operational")
    operational_components = set(component["name"] for component in components if component["status"] == "operational")
    
    for customer in customers:
        customer_tags = set(customer["groups"])
        
        if "any" in customer_tags or "all" in customer_tags or customer_tags & incident_components or customer_tags & operational_components:
            affected_customers.append(customer)
    
    # Update affected components memory
    affected_components[page_id] = [component["name"] for component in components if component["status"] != "operational"]
    save_affected_components(affected_components)
    
    return affected_customers, incident_components, operational_components

def notify_customer(customer, update, update_type, incident_components, operational_components):
    if update_type == "status":
        for statuspage in statuspages:
            if not statuspage.get("enabled", True):
                continue

            affected_customers, incident_components, operational_components = match_customers_to_incident(statuspage['api_key'], statuspage['page_id'], update, affected_components)
            if customer not in affected_customers:
                continue

            if customer["discord"]["enabled"]:
                message = format_status_for_discord(update, customer, config)
                send_discord_message(customer["discord"]["webhook_url"], message, config)
                logger.info(f"Sent Discord message to {customer['name']}")
            
            if customer["slack"]["enabled"]:
                message_blocks = format_status_for_slack(update, customer, config)
                send_slack_message(customer["slack"]["webhook_url"], message_blocks, update['status'], config)
                logger.info(f"Sent Slack message to {customer['name']}")
            
            if customer["telegram"]["enabled"]:
                message = format_status_for_telegram(update, customer, config)
                send_telegram_message_sync(customer["telegram"]["bot_token"], customer["telegram"]["chat_id"], message, config)
                logger.info(f"Sent Telegram message to {customer['name']}")
            
            if customer["statuspage"]["enabled"]:
                message = format_status_for_statuspage(update, customer, config)
                update_statuspage(customer["statuspage"]["api_key"], customer["statuspage"]["page_id"], message)
                logger.info(f"Updated Statuspage for {customer['name']}")
    elif update_type == "governance":
        if customer["discord"]["enabled"]:
            message = format_governance_for_discord(update, customer, config)
            send_discord_message(customer["discord"]["webhook_url"], message, config)
            logger.info(f"Sent Discord message to {customer['name']}")
        
        if customer["slack"]["enabled"]:
            message_blocks = format_governance_for_slack(update, customer, config)
            send_slack_message(customer["slack"]["webhook_url"], message_blocks, update['status'], config)
            logger.info(f"Sent Slack message to {customer['name']}")
        
        if customer["telegram"]["enabled"]:
            message = format_governance_for_telegram(update, customer, config)
            send_telegram_message_sync(customer["telegram"]["bot_token"], customer["telegram"]["chat_id"], message, config)
            logger.info(f"Sent Telegram message to {customer['name']}")

def main(override_date_filter):
    global config, config_mtime, avatar_url, statuspages, customers, affected_components

    sent_updates = load_sent_updates()
    today = datetime.now().date()
    
    for statuspage in statuspages:
        if not statuspage.get("enabled", True):
            continue

        updates = fetch_status_updates(statuspage["api_key"], statuspage["page_id"])
        formatted_updates = [format_status_update(update) for update in updates]
        proposals = fetch_governance_proposals()
        
        if override_date_filter:
            new_updates = [formatted_updates[0]] if formatted_updates else []
            new_proposals = [proposals[0]] if proposals else []
            logger.info("Override date filter: Sending the latest update and proposal regardless of date")
        else:
            new_updates = []
            for update in formatted_updates:
                try:
                    update_hash = hash_data(update)
                    if update_hash not in sent_updates and (isoparse(update["created_at"]).date() == today or isoparse(update["updated_at"]).date() == today):
                        new_updates.append(update)
                except (ParserError, ValueError) as e:
                    logger.error(f"Failed to parse date for update {update['id']}: {e}")

            new_proposals = []
            for proposal in proposals:
                try:
                    proposal_hash = hash_data(proposal)
                    if proposal_hash not in sent_updates and isoparse(proposal['submit_time']).date() == today:
                        new_proposals.append(proposal)
                except (ParserError, ValueError) as e:
                    logger.error(f"Failed to parse date for proposal {proposal['id']}: {e}")

        if new_updates or new_proposals:
            for update in new_updates:
                for customer in customers:
                    if customer["enable"]:
                        affected_customers, incident_components, operational_components = match_customers_to_incident(statuspage['api_key'], statuspage['page_id'], update, affected_components)
                        notify_customer(customer, update, "status", incident_components, operational_components)
                        update_hash = hash_data(update)
                        sent_updates.add(update_hash)
                        logger.info(f"Notified {customer['name']} about status update {update['title']}")
            
            for proposal in new_proposals:
                formatted_proposal = format_governance_proposal(proposal)
                for customer in customers:
                    if customer["enable"]:
                        notify_customer(customer, formatted_proposal, "governance", set(), set())
                        proposal_hash = hash_data(proposal)
                        sent_updates.add(proposal_hash)
                        logger.info(f"Notified {customer['name']} about governance proposal {proposal['title']}")
            
            save_sent_updates(sent_updates)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Notifier script for ZetaChain updates and proposals")
    parser.add_argument('--override-date-filter', action='store_true', help="Override date filter and send the latest update and proposal regardless of date")
    parser.add_argument('--once', action='store_true', help="Run the script once and exit")
    parser.add_argument('--watch', action='store_true', help="Keep the script running and check for updates every 30 seconds")
    parser.add_argument('--loglevel', default='info', choices=['debug', 'info', 'warning', 'error', 'critical'], help="Set the logging level")
    args = parser.parse_args()

    logger.remove()
    logger.add(lambda msg: print(msg, end=''), level=args.loglevel.upper(), colorize=True)

    if not any(vars(args).values()):
        parser.print_help()
    else:
        logger.info("Starting notifier script")
        if args.once:
            main(args.override_date_filter)
        elif args.watch:
            while True:
                current_mtime = get_config_mtime()
                if current_mtime != config_mtime:
                    logger.info("Detected changes in config.yaml, reloading configuration")
                    config = load_config()
                    config_mtime = current_mtime
                    avatar_url = config['avatar_url']
                    statuspages = config['statuspages']
                    customers = config['customers']
                    affected_components = load_affected_components()
                main(args.override_date_filter)
                time.sleep(30)
        logger.info("Notifier script finished")