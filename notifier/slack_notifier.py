import textwrap
import requests
from loguru import logger

def format_status_for_slack(update, customer, config):
    tags_text = ", ".join([f"`{tag}`" for tag in customer["groups"]])
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": textwrap.dedent(f"""
                            Hi {customer['name']}
                            
                            *Status Update: {update['title']}*
                            {update['latest_update']}
                            
                            *Status:* {update['status']}
                            *Impact:* {update['impact']}
                            *Link:* {update['link']}
                        """)
            }
        }, 
        { 
            "type": "divider" 
        }, 
        { 
            "type": "context", 
            "elements": [ 
                { "type": "mrkdwn", "text": f"Sent via Zetachain Community Notifier\n\nTags: {tags_text}" } 
            ] 
        }, 
        { 
            "type": "divider" 
        }
    ]

def format_governance_for_slack(proposal, customer, config):
    tags_text = ", ".join([f"`{tag}`" for tag in customer["groups"]])
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": textwrap.dedent(f"""
                            Hi {customer['name']}

                            {proposal['status_icon']} *Governance Proposal: #{proposal['id']} - {proposal['title']}*
                            
                            {proposal['summary']}
                            
                            *Status:* {proposal['status']}
                            *Type:* {proposal['type']}
                            *Submit Time:* {proposal['submit_time']}
                            *Deposit End Time:* {proposal['deposit_end_time']}
                            *Voting End Time:* {proposal['voting_end_time']}
                        """)
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Yes*\n{proposal['yes_percentage']:.2f}%\n{proposal['yes_count']:,.2f} ZETA"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*No*\n{proposal['no_percentage']:.2f}%\n{proposal['no_count']:,.2f} ZETA"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Abstain*\n{proposal['abstain_percentage']:.2f}%\n{proposal['abstain_count']:,.2f} ZETA"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*No with Veto*\n{proposal['no_with_veto_percentage']:.2f}%\n{proposal['no_with_veto_count']:,.2f} ZETA"
                }
            ]
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"More details: {proposal['proposal_link']}\n"
            }
        }, 
        { 
            "type": "divider" 
        }, 
        { 
            "type": "context", 
            "elements": [ 
                { "type": "mrkdwn", "text": f"Sent via Zetachain Community Notifier\n\nTags: {tags_text}" } 
            ] 
        }, 
        { 
            "type": "divider" 
        }
    ]

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

def send_slack_message(webhook_url, message_blocks, status, config):
    color = get_color_based_on_status(status)
    data = {
        "username": "Zetachain Notifier",
        "icon_url": config['avatar_url'],  # Use the avatar URL from the config
        "attachments": [
            {
                "color": color,  # Use the dynamic color
                "blocks": message_blocks
            }
        ]
    }
    response = requests.post(webhook_url, json=data)
    logger.info(f"Sent Slack message with status code {response.status_code}")
    return response.status_code