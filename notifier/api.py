from flask import Flask, request, jsonify
from loguru import logger
from fetch_updates import fetch_broadcast
from format_updates import format_governance_proposal, format_broadcast_for_discord, format_broadcast_for_slack, format_broadcast_for_telegram
from utils import load_sent_updates, save_sent_updates
from config import load_config
from notify import notify_customer

app = Flask(__name__)

config = load_config()
customers = config['customers']
sent_updates = load_sent_updates()

@app.route('/broadcast', methods=['POST'])
def broadcast():
    data = request.json
    component = data.get('component')
    message = data.get('message')
    proposal_id = data.get('proposal_id')
    
    if not component or not message:
        logger.error("Component and message are required")
        return jsonify({"error": "Component and message are required"}), 400

    update_type = "governance" if proposal_id else "broadcast"
    custom_message = f"Custom Broadcast: {message}"

    if update_type == "governance":
        proposal = fetch_broadcast(proposal_id)
        if proposal:
            formatted_proposal = format_governance_proposal(proposal)
            for customer in customers:
                if customer["enable"]:
                    notify_customer(customer, formatted_proposal, update_type, config)
                    sent_updates.add(proposal_id)
                    logger.info(f"Notified {customer['name']} about governance proposal {proposal_id}")
        else:
            logger.error("Proposal not found")
            return jsonify({"error": "Proposal not found"}), 404
    else:
        for customer in customers:
            if customer["enable"]:
                if customer["discord"]["enabled"]:
                    message = format_broadcast_for_discord(custom_message, customer, config)
                    notify_customer(customer, message, "broadcast", config)
                    logger.info(f"Sent Broadcast Discord message to {customer['name']}")
                
                if customer["slack"]["enabled"]:
                    message_blocks = format_broadcast_for_slack(custom_message, customer, config)
                    notify_customer(customer, message_blocks, "broadcast", config)
                    logger.info(f"Sent Broadcast Slack message to {customer['name']}")
                
                if customer["telegram"]["enabled"]:
                    message = format_broadcast_for_telegram(custom_message, customer, config)
                    notify_customer(customer, message, "broadcast", config)
                    logger.info(f"Sent Broadcast Telegram message to {customer['name']}")

    save_sent_updates(sent_updates)
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(port=5000)