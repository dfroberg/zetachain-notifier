import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='urllib3')

import pickle
import os
import requests
import argparse
import humanize
import yaml
from datetime import datetime
from dateutil.parser import isoparse
from discord_notifier import send_discord_message, format_governance_for_discord, format_status_for_discord
from slack_notifier import send_slack_message, format_governance_for_slack, format_status_for_slack
from telegram_notifier import send_telegram_message_sync, format_governance_for_telegram, format_status_for_telegram
from statuspage_notifier import update_statuspage, format_governance_for_statuspage, format_status_for_statuspage
from loguru import logger
import time

PICKLE_FILE = 'sent_updates.pkl'

def load_config():
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    return config

config = load_config()
avatar_url = config['avatar_url']
statuspages = config['statuspages']
customers = config['customers']

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
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        logger.info("Fetched status updates")
        return response.json()
    logger.error("Failed to fetch status updates")
    return []

def format_status_update(incident):
    latest_update = incident["incident_updates"][0] if incident["incident_updates"] else {}
    created_at = humanize.naturaltime(isoparse(incident["created_at"]))
    updated_at = humanize.naturaltime(isoparse(incident["updated_at"]))
    resolved_at = humanize.naturaltime(isoparse(incident.get("resolved_at")))
    formatted_update = {
        "id": incident["id"],
        "title": incident["name"],
        "link": incident["shortlink"],
        "status": incident["status"],
        "created_at": created_at,
        "updated_at": updated_at,
        "resolved_at": resolved_at,
        "impact": incident["impact"],
        "latest_update": latest_update.get('body', 'No updates available.')
    }
    return formatted_update

def fetch_governance_proposals():
    url = 'https://zetachain.blockpi.network/lcd/v1/public/cosmos/gov/v1/proposals?proposal_status=PROPOSAL_STATUS_UNSPECIFIED&pagination.count_total=true&pagination.reverse=true'
    headers = {'accept': 'application/json'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        logger.info("Fetched governance proposals")
        return response.json().get('proposals', [])
    logger.error("Failed to fetch governance proposals")
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

    submit_time =  humanize.naturaltime(isoparse(proposal['submit_time']))
    deposit_end_time =  humanize.naturaltime(isoparse(proposal['deposit_end_time']))
    voting_end_time =  humanize.naturaltime(isoparse(proposal['voting_end_time']))
    
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

def notify_customer(customer, update, update_type):
    if update_type == "status":
        if customer["discord"]["enabled"]:
            message = format_status_for_discord(update, customer, config)
            send_discord_message(customer["discord"]["webhook_url"], message, config)
            logger.info(f"Sent Discord message to {customer['name']}")
        
        if customer["slack"]["enabled"]:
            message_blocks = format_status_for_slack(update, customer, config)
            send_slack_message(customer["slack"]["webhook_url"], message_blocks, config)
            logger.info(f"Sent Slack message to {customer['name']}")
        
        if customer["telegram"]["enabled"]:
            message = format_status_for_telegram(update, customer, config)
            send_telegram_message_sync(customer["telegram"]["bot_token"], customer["telegram"]["chat_id"], message, config)
            logger.info(f"Sent Telegram message to {customer['name']}")
        
        if customer["statuspage"]["enabled"]:
            message = format_status_for_statuspage(update, customer, config)
            update_statuspage(customer["statuspage"]["api_key"], customer["statuspage"]["page_id"], message, config)
            logger.info(f"Updated Statuspage for {customer['name']}")
    elif update_type == "governance":
        if customer["discord"]["enabled"]:
            message = format_governance_for_discord(update, customer, config)
            send_discord_message(customer["discord"]["webhook_url"], message, config)
            logger.info(f"Sent Discord message to {customer['name']}")
        
        if customer["slack"]["enabled"]:
            message_blocks = format_governance_for_slack(update, customer, config)
            send_slack_message(customer["slack"]["webhook_url"], message_blocks, config)
            logger.info(f"Sent Slack message to {customer['name']}")
        
        if customer["telegram"]["enabled"]:
            message = format_governance_for_telegram(update, customer, config)
            send_telegram_message_sync(customer["telegram"]["bot_token"], customer["telegram"]["chat_id"], message, config)
            logger.info(f"Sent Telegram message to {customer['name']}")
        
        if customer["statuspage"]["enabled"]:
            message = format_governance_for_statuspage(update, customer, config)
            update_statuspage(customer["statuspage"]["api_key"], customer["statuspage"]["page_id"], message, config)
            logger.info(f"Updated Statuspage for {customer['name']}")

def main(override_date_filter):
    sent_updates = load_sent_updates()
    statuspage = statuspages[0]  # Assuming you want to use the first statuspage configuration
    updates = fetch_status_updates(statuspage["api_key"], statuspage["page_id"])
    formatted_updates = [format_status_update(update) for update in updates]
    proposals = fetch_governance_proposals()
    today = datetime.now().date()
    
    if override_date_filter:
        new_updates = [formatted_updates[0]] if formatted_updates else []
        new_proposals = [proposals[0]] if proposals else []
        logger.info("Override date filter: Sending the latest update and proposal regardless of date")
    else:
        new_updates = [update for update in formatted_updates if update["id"] not in sent_updates and isoparse(update["created_at"]).date() == today]
        new_proposals = [proposal for proposal in proposals if proposal['id'] not in sent_updates and isoparse(proposal['submit_time']).date() == today]

    if new_updates or new_proposals:
        for update in new_updates:
            for customer in customers:
                if customer["enable"]:
                    notify_customer(customer, update, "status")
                    sent_updates.add(update["id"])
                    logger.info(f"Notified {customer['name']} about status update {update['title']}")
        
        for proposal in new_proposals:
            formatted_proposal = format_governance_proposal(proposal)
            for customer in customers:
                if customer["enable"]:
                    notify_customer(customer, formatted_proposal, "governance")
                    sent_updates.add(proposal['id'])
                    logger.info(f"Notified {customer['name']} about governance proposal {proposal['title']}")
        
        save_sent_updates(sent_updates)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Notifier script for ZetaChain updates and proposals")
    parser.add_argument('--override-date-filter', action='store_true', help="Override date filter and send the latest update and proposal regardless of date")
    parser.add_argument('--once', action='store_true', help="Run the script once and exit")
    parser.add_argument('--watch', action='store_true', help="Keep the script running and check for updates every 30 seconds")
    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
    else:
        logger.info("Starting notifier script")
        if args.once:
            main(args.override_date_filter)
        elif args.watch:
            while True:
                main(args.override_date_filter)
                time.sleep(30)
        logger.info("Notifier script finished")