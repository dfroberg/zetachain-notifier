import textwrap
import asyncio
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError
from loguru import logger

def format_status_for_telegram(update, customer, config):
    try:
        return textwrap.dedent(f"""
            Hi {customer['name']}

            *Status Update: {update['title']}*
            {update['latest_update']}

            *Status:* {update['status']}
            *Impact:* {update['impact']}
            *Link:* {update['link']}

            Sent via Zetachain Community Notifier
            Tags: {', '.join([f'`{tag}`' for tag in customer['groups']])}
        """)
    except KeyError as e:
        logger.error(f"Missing key in data: {e}")
        return "Error: Missing data for status update."

def format_governance_for_telegram(proposal, customer, config):
    try:
        tags_text = ", ".join([f"`{tag}`" for tag in customer["groups"]])
        return textwrap.dedent(f"""
            Hi {customer['name']}

            {proposal['status_icon']} *Governance Proposal: #{proposal['id']} - {proposal['title']}*
            {proposal['summary']}

            *Status:* {proposal['status']}
            *Type:* {proposal['type']}
            *Submit Time:* {proposal['submit_time']}
            *Deposit End Time:* {proposal['deposit_end_time']}
            *Voting End Time:* {proposal['voting_end_time']}
            Votes Tallies:
            *Yes*
            {proposal['yes_percentage']:.2f}%
            {proposal['yes_count']:,.2f} ZETA

            *No*
            {proposal['no_percentage']:.2f}%
            {proposal['no_count']:,.2f} ZETA

            *Abstain*
            {proposal['abstain_percentage']:.2f}%
            {proposal['abstain_count']:,.2f} ZETA

            *No with Veto*
            {proposal['no_with_veto_percentage']:.2f}%
            {proposal['no_with_veto_count']:,.2f} ZETA
            More details: {proposal['proposal_link']}

            Sent via Zetachain Community Notifier
            Tags: {tags_text}
        """)
    except KeyError as e:
        logger.error(f"Missing key in input data: {e}")
        return "Error: Missing data for proposal or customer."

async def send_telegram_message(bot_token: str, chat_id: int, message: str, config: dict) -> bool:
    async with Bot(token=bot_token) as bot:
        max_retries = config.get('max_retries', 3)
        retry_delay = config.get('retry_delay', 1)
        for attempt in range(max_retries):
            try:
                response = await bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN)
                logger.info(f"Sent Telegram message with message_id {response.message_id}")
                return True
            except TelegramError as e:
                logger.error(f"Attempt {attempt + 1} failed to send Telegram message: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
    return False

def send_telegram_message_sync(bot_token, chat_id, message, config):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(send_telegram_message(bot_token, chat_id, message, config))
