import requests
from loguru import logger

def format_status_for_discord(update, customer, config):
    avatar_url = config['avatar_url']
    # Set color based on update['status'] value
    if update['status'] == 'investigating':
        color = 0xffa500 # Orange color
    elif update['status'] == 'resolved':
        color = 0x00ff00 # Green color
    elif update['status'] == 'under investigation':
        color = 0xffff00 # Yellow color
    elif update['status'] == 'new':
        color = 0x0000ff # Blue color
    elif update['status'] == 'postmortem':
        color = 0x800080 # Purple color
    elif update['status'] == 'scheduled':
        color = 0x808080 # Gray color
    elif update['status'] == 'monitoring':
        color = 0xffa500 # Orange color
    else:
        color = 0x000000 # Black color

    embed = {
        "author": {
            "name": "Zetachain Community Notifier",
            "icon_url": avatar_url
        },
        "title": f"Status Update: {update['title']}",
        "description": update['latest_update'],
        "color": color,
        "fields": [
            {"name": "Status", "value": update['status'], "inline": True},
            {"name": "Impact", "value": update['impact'], "inline": True},
            {"name": "Link", "value": update['link'], "inline": False}
        ],
        "footer": {
            "text": f"Sent via Zetachain Community Notifier\nTags: {', '.join([f'`{tag}`' for tag in customer['groups']])}"
        }
    }
    return embed

def format_governance_for_discord(proposal, customer, config):
    avatar_url = config['avatar_url']
    # Set color based on proposal['status'] value
    if proposal['status'] == 'PROPOSAL_STATUS_REJECTED':
        color = 0xff0000 # Red color
    elif proposal['status'] == 'PROPOSAL_STATUS_ACCEPTED':
        color = 0x00ff00 # Green color
    elif proposal['status'] == 'PROPOSAL_STATUS_UNSPECIFIED':
        color = 0xffff00 # Yellow color
    else:
        color = 0x000000 # Black color

    embed = {
        "author": {
            "name": "Zetachain Community Notifier",
            "icon_url": avatar_url
        },
        "title": f"{proposal['status_icon']} Governance Proposal: #{proposal['id']} - {proposal['title']}",
        "description": proposal['summary'],
        "color": 0x0000ff,  # Blue color
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
    response = requests.post(webhook_url, json=data)
    logger.info(f"Sent Discord message with status code {response.status_code}")
    return response.status_code