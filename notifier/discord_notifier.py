import requests
from loguru import logger
from utils import get_color_based_on_status

def format_status_for_discord(update, customer, config):
    # Ensure all fields are correctly formatted
    embed = {
        "author": {"name": "Zetachain Community Notifier", "icon_url": config['avatar_url']},
        "title": f"Status Update: {update['title']}",
        "description": update['latest_update'],
        "color": get_color_based_on_status(update['status']),
        "fields": [
            {"name": "Status", "value": update['status'], "inline": True},
            {"name": "Impact", "value": update['impact'], "inline": True},
            {"name": "Link", "value": update['link'], "inline": False}
        ],
        "footer": {"text": f"Sent via Zetachain Community Notifier\nTags: {', '.join([f'`{tag}`' for tag in customer['groups']])}"}
    }
    return embed

def format_governance_for_discord(proposal, customer, config):
    avatar_url = config['avatar_url']
    # Set color based on proposal['status'] value
    color = get_color_based_on_status(proposal['status'])

    embed = {
        "author": {
            "name": "Zetachain Community Notifier",
            "icon_url": avatar_url
        },
        "title": f"{proposal['status_icon']} Governance Proposal: #{proposal['id']} - {proposal['title']}",
        "description": proposal['summary'],
        "color": color, # Use the color based on the proposal status
        "fields": [
            {"name": "Status", "value": proposal['status'], "inline": True},
            {"name": "Type", "value": proposal['type'], "inline": True},
            {"name": "Submit Time", "value": proposal['submit_time_display'], "inline": False},
            {"name": "Deposit End Time", "value": proposal['deposit_end_time_display'], "inline": False},
            {"name": "Voting End Time", "value": proposal['voting_end_time_display'], "inline": False},
            {"name": "Yes", "value": f"{proposal['yes_percentage']:.2f}%\n{proposal['yes_count']:,.2f} ZETA", "inline": True},
            {"name": "No", "value": f"{proposal['no_percentage']:.2f}%\n{proposal['no_count']:,.2f} ZETA", "inline": True},
            {"name": "Abstain", "value": f"{proposal['abstain_percentage']:.2f}%\n{proposal['abstain_count']:,.2f} ZETA", "inline": True},
            {"name": "No with Veto", "value": f"{proposal['no_with_veto_percentage']:.2f}%\n{proposal['no_with_veto_count']:,.2f} ZETA", "inline": True},
            {"name": "More details", "value": proposal['proposal_link'], "inline": False}
        ],
        "footer": {
            "text": f"Sent via Zetachain Community Notifier\nTags: {', '.join([f'`{tag}`' for tag in customer['groups']])}"
        }
    }
    return embed

def send_discord_message(webhook_url, embed, config):
    data = {"embeds": [embed]}
    logger.debug(f"Sending Discord message to {webhook_url}")
    logger.debug(f"Message data: {data}")
    response = requests.post(webhook_url, json=data)
    logger.info(f"Sent Discord message with status code {response.status_code}")
    logger.debug(f"Response content: {response.content}")
    return response.status_code
