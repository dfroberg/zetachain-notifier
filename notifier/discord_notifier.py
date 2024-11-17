import requests
from loguru import logger

def get_color_based_on_status(status):
    # Statuspage statuses
    if status == 'investigating':
        return "#ffa500"  # Orange color
    elif status == 'resolved':
        return "#00ff00"  # Green color
    elif status == 'under investigation':
        return "#ffff00"  # Yellow color
    elif status == 'identified':
        return "#FF8C00"  # Dark Orange color
    elif status == 'new':
        return "#0000ff"  # Blue color
    elif status == 'postmortem':
        return "#800080"  # Purple color
    elif status == 'scheduled':
        return "#808080"  # Gray color
    elif status == 'monitoring':
        return "#90EE90"  # Lights green color
    # Governance proposal statuses
    elif status == 'PROPOSAL_STATUS_REJECTED':
        return 0xff0000 # Red color
    elif status == 'PROPOSAL_STATUS_ACCEPTED':
        return 0x00ff00 # Green color
    elif status == 'PROPOSAL_STATUS_UNSPECIFIED':
        return 0xffff00 # Yellow color
    # Default color
    else:
        return "#000000"  # Black color
    
def format_status_for_discord(update, customer, config):
    avatar_url = config['avatar_url']
    # Set color based on update['status'] value
    color = get_color_based_on_status(update['status'])

    embed = {
        "author": {
            "name": "Zetachain Community Notifier",
            "icon_url": avatar_url
        },
        "title": f"Status Update: {update['title']}",
        "description": update['latest_update'],
        "color": color, # Use the color based on the update status
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
    response = requests.post(webhook_url, json=data)
    logger.info(f"Sent Discord message with status code {response.status_code}")
    return response.status_code