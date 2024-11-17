import asyncio
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError
from loguru import logger

def format_status_for_telegram(update, customer, config):
    return (
        f"Hi {customer['name']}\n\n"
        f"*Status Update: {update['title']}*\n"
        f"{update['latest_update']}\n\n"
        f"*Status:* {update['status']}\n"
        f"*Impact:* {update['impact']}\n"
        f"*Link:* {update['link']}\n"
        f"\nSent via Zetachain Community Notifier\n"
        f"Tags: {', '.join([f'`{tag}`' for tag in customer['groups']])}"
    )

def format_governance_for_telegram(proposal, customer, config):
    tags_text = ", ".join([f"`{tag}`" for tag in customer["groups"]])
    return (
        f"Hi {customer['name']}\n\n"
        f"{proposal['status_icon']} *Governance Proposal: #{proposal['id']} - {proposal['title']}*\n"
        f"{proposal['summary']}\n\n"
        f"*Status:* {proposal['status']}\n"
        f"*Type:* {proposal['type']}\n"
        f"*Submit Time:* {proposal['submit_time']}\n"
        f"*Deposit End Time:* {proposal['deposit_end_time']}\n"
        f"*Voting End Time:* {proposal['voting_end_time']}\n"
        "Votes Tallies:\n"
        f"*Yes*\n{proposal['yes_percentage']:.2f}%\n{proposal['yes_count']:,.2f} ZETA\n\n"
        f"*No*\n{proposal['no_percentage']:.2f}%\n{proposal['no_count']:,.2f} ZETA\n\n"
        f"*Abstain*\n{proposal['abstain_percentage']:.2f}%\n{proposal['abstain_count']:,.2f} ZETA\n\n"
        f"*No with Veto*\n{proposal['no_with_veto_percentage']:.2f}%\n{proposal['no_with_veto_count']:,.2f} ZETA\n"
        f"More details: {proposal['proposal_link']}\n"
        f"\nSent via Zetachain Community Notifier\n"
        f"Tags: {tags_text}"
    )

async def send_telegram_message(bot_token, chat_id, message, config):
    bot = Bot(token=bot_token)
    try:
        response = await bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN)
        logger.info(f"Sent Telegram message with message_id {response.message_id}")
    except TelegramError as e:
        logger.error(f"Failed to send Telegram message: {e.message}")
        return False
    return True

def send_telegram_message_sync(bot_token, chat_id, message, config):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(send_telegram_message(bot_token, chat_id, message, config))

async def get_chat_id_by_name(bot_token, name):
    bot = Bot(token=bot_token)
    updates = await bot.get_updates()
    for update in updates:
        if update.message and update.message.chat:
            logger.debug(f"Found chat: {update.message.chat}")
            if update.message.chat.username == name:
                return update.message.chat.id
    logger.error(f"Chat ID for name '{name}' not found")
    return None

def get_chat_id_by_name_sync(bot_token, name):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(get_chat_id_by_name(bot_token, name))