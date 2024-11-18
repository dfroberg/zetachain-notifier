import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='urllib3')

import argparse
import time
from datetime import datetime
from loguru import logger
from dateutil.parser import isoparse, ParserError
from config import config, config_mtime, avatar_url, statuspages, customers, get_config_mtime, load_config
from utils import load_sent_updates, save_sent_updates, load_affected_components, save_affected_components, hash_data
from fetch_updates import fetch_status_updates, fetch_statuspage_components, fetch_governance_proposals
from format_updates import format_status_update, format_governance_proposal
from notify import notify_customer
from api import app
import threading

def run_api():
    app.run(port=5000)

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
                        notify_customer(customer, update, "status", config)
                        sent_updates.add(update["id"])
                        logger.info(f"Notified {customer['name']} about status update {update['title']}")
            
            for proposal in new_proposals:
                formatted_proposal = format_governance_proposal(proposal)
                for customer in customers:
                    if customer["enable"]:
                        notify_customer(customer, formatted_proposal, "governance", config)
                        sent_updates.add(proposal['id'])
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
            api_thread = threading.Thread(target=run_api)
            api_thread.daemon = True
            api_thread.start()
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