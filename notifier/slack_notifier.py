import requests
from loguru import logger

def format_status_for_slack(update, customer):
    tags_text = ", ".join([f"`{tag}`" for tag in customer["groups"]])
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Hi {customer['name']}\n\n*Status Update: {update['title']}*\n{update['latest_update']}\n\n*Status:* {update['status']}\n*Impact:* {update['impact']}\n*Link:* {update['link']}\n"
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

def format_governance_for_slack(proposal, customer):
    tags_text = ", ".join([f"`{tag}`" for tag in customer["groups"]])
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Hi {customer['name']}\n\n{proposal['status_icon']} *Governance Proposal: #{proposal['id']} - {proposal['title']}*\n{proposal['summary']}\n\n*Status:* {proposal['status']}\n*Type:* {proposal['type']}\n*Submit Time:* {proposal['submit_time']}\n*Deposit End Time:* {proposal['deposit_end_time']}\n*Voting End Time:* {proposal['voting_end_time']}\n"
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

def send_slack_message(webhook_url, message_blocks):
    data = {
        "username": "Zetachain Notifier",
        "icon_url": "https://avatars.githubusercontent.com/u/86979844?s=200&v=4",  # Replace with your icon URL
        "blocks": message_blocks
    }
    response = requests.post(webhook_url, json=data)
    logger.info(f"Sent Slack message with status code {response.status_code}")
    return response.status_code