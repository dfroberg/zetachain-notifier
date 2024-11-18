from discord_notifier import send_discord_message, format_governance_for_discord, format_status_for_discord
from slack_notifier import send_slack_message, format_governance_for_slack, format_status_for_slack
from telegram_notifier import send_telegram_message_sync, format_governance_for_telegram, format_status_for_telegram
from statuspage_notifier import update_statuspage, format_status_for_statuspage
from loguru import logger

def notify_customer(customer, update, update_type, config):
    if update_type == "status":
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
    elif update_type == "broadcast":
        if customer["discord"]["enabled"]:
            message = format_status_for_discord(update, customer, config)
            send_discord_message(customer["discord"]["webhook_url"], message, config)
            logger.info(f"Sent Broadcast Discord message to {customer['name']}")
        
        if customer["slack"]["enabled"]:
            message_blocks = format_status_for_slack(update, customer, config)
            send_slack_message(customer["slack"]["webhook_url"], message_blocks, update['status'], config)
            logger.info(f"Sent Broadcast Slack message to {customer['name']}")
        
        if customer["telegram"]["enabled"]:
            message = format_status_for_telegram(update, customer, config)
            send_telegram_message_sync(customer["telegram"]["bot_token"], customer["telegram"]["chat_id"], message, config)
            logger.info(f"Sent Broadcast Telegram message to {customer['name']}")
