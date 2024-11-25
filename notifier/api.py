from flask import Flask, request, jsonify
from loguru import logger
from fetch_updates import fetch_broadcast
from format_updates import format_governance_proposal, format_broadcast_for_discord, format_broadcast_for_slack, format_broadcast_for_telegram, format_governance_broadcast_for_discord, format_governance_broadcast_for_slack, format_governance_broadcast_for_telegram
from discord_notifier import send_discord_message
from slack_notifier import send_slack_message
from telegram_notifier import send_telegram_message_sync
from utils import load_sent_updates, save_sent_updates, hash_data
from config import load_config
from notify import notify_customer

app = Flask(__name__)

config = load_config()
broadcast_config = config.get('broadcast', {})
customers = config['customers']
sent_updates = load_sent_updates()

def match_customers_to_update(update_tags, customers):
    affected_customers = []
    update_tags = set(update_tags)
    for customer in customers:
        customer_tags = set(customer["groups"])
        if "any" in customer_tags or "all" in customer_tags or customer_tags & update_tags:
            affected_customers.append(customer)
            logger.debug(f"Matched customer {customer['name']} to broadcast tags {update_tags}") if customer["enable"] else logger.debug(f"Matched customer {customer['name']} to broadcast {update_tags} (disabled)")
        else:
            logger.debug(f"Did not match customer {customer['name']} to broadcast tags {update_tags}") if customer["enable"] else logger.debug(f"Did not match customer {customer['name']} to broadcast {update_tags} (disabled)")
            logger.debug(f"Customer tags: {customer_tags}")
            logger.debug(f"Update tags: {update_tags}") if update_tags else logger.debug(f"Broadcast tags: None")
    return affected_customers

@app.route('/broadcast', methods=['POST'])
def broadcast():
    if not broadcast_config.get('enabled', False):
        logger.error("Broadcasting is disabled")
        return jsonify({"error": "Broadcasting is disabled"}), 403
    data = request.json
    component = set(data.get('component').split(','))
    message = data.get('message')
    proposal_id = data.get('proposal_id')
    
    if not component or not message:
        logger.error("Component and message are required")
        return jsonify({"error": "Component and message are required"}), 400

    update_type = "governance" if proposal_id else "broadcast"
    custom_message = f"{message}"
    sent_updates = load_sent_updates()
    # Fetch proposal if proposal_id is provided
    if update_type == "governance":
        proposal = fetch_broadcast(proposal_id)
        if proposal:
            formatted_proposal = format_governance_proposal(proposal)
            affected_customers = match_customers_to_update(component, customers)
            for customer in affected_customers:
                if customer["enable"]:
                    if customer.get("discord", {}).get("enabled", False):
                        message = format_governance_broadcast_for_discord(custom_message, formatted_proposal, customer, config)
                        update_hash = hash_data(message)
                        if update_hash not in sent_updates:
                            send_discord_message(customer["discord"]["webhook_url"], message, config)
                            sent_updates.add(update_hash) # Lets not send again unless it changes
                            logger.info(f"Sent Broadcast Discord message to {customer['name']}")
                        else:
                            logger.info(f"Broadcast Discord message already sent to {customer['name']}")
                    
                    if customer.get("slack", {}).get("enabled", False):
                        message_blocks = format_governance_broadcast_for_slack(custom_message, formatted_proposal, customer, config)
                        update_hash = hash_data(message_blocks)
                        if update_hash not in sent_updates:
                            send_slack_message(customer["slack"]["webhook_url"], message_blocks, "new", config)
                            sent_updates.add(update_hash)
                            logger.info(f"Sent Broadcast Slack message to {customer['name']}")
                        else:
                            logger.info(f"Broadcast Slack message already sent to {customer['name']}")
                    
                    if customer.get("telegram", {}).get("enabled", False):
                        message = format_governance_broadcast_for_telegram(custom_message, formatted_proposal, customer, config)
                        update_hash = hash_data(message)
                        if update_hash not in sent_updates:
                            send_telegram_message_sync(customer["telegram"]["bot_token"], customer["telegram"]["chat_id"], message, config)
                            sent_updates.add(update_hash) # Lets not send again unless it changes
                            logger.info(f"Sent Broadcast Telegram message to {customer['name']}")
                        else:
                            logger.info(f"Broadcast Telegram message already sent to {customer['name']}")
        else:
            logger.error("Proposal not found")
            return jsonify({"error": "Proposal not found"}), 404
    else:
        affected_customers = match_customers_to_update(component, customers)
        for customer in affected_customers:
            if customer["enable"]:
                if customer.get("discord", {}).get("enabled", False):
                    message = format_broadcast_for_discord(custom_message, customer, config)
                    update_hash = hash_data(message)
                    if update_hash not in sent_updates:
                        send_discord_message(customer["discord"]["webhook_url"], message, config)
                        sent_updates.add(update_hash)
                        logger.info(f"Sent Broadcast Discord message to {customer['name']}")
                    else:
                        logger.info(f"Broadcast Discord message already sent to {customer['name']}")
                
                if customer.get("slack", {}).get("enabled", False):
                    message_blocks = format_broadcast_for_slack(custom_message, customer, config)
                    update_hash = hash_data(message_blocks)
                    if update_hash not in sent_updates:
                        send_slack_message(customer["slack"]["webhook_url"], message_blocks, "new", config)
                        sent_updates.add(update_hash)
                        logger.info(f"Sent Broadcast Slack message to {customer['name']}")
                    else:
                        logger.info(f"Broadcast Slack message already sent to {customer['name']}")
                
                if customer.get("telegram", {}).get("enabled", False):
                    message = format_broadcast_for_telegram(custom_message, customer, config)
                    update_hash = hash_data(message)
                    if update_hash not in sent_updates:
                        send_telegram_message_sync(customer["telegram"]["bot_token"], customer["telegram"]["chat_id"], message, config)
                        sent_updates.add(update_hash) # Lets not send again unless it changes
                        logger.info(f"Sent Broadcast Telegram message to {customer['name']}")
                    else:
                        logger.info(f"Broadcast Telegram message already sent to {customer['name']}")
                        
    save_sent_updates(sent_updates)
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(port=5000)