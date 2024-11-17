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

def send_slack_message(webhook_url, message_blocks, config):
    data = {
        "username": "Zetachain Notifier",
        "icon_url": "https://avatars.githubusercontent.com/u/86979844?s=200&v=4",  # Replace with your icon URL
        "blocks": message_blocks
    }
    response = requests.post(webhook_url, json=data)
    logger.info(f"Sent Slack message with status code {response.status_code}")
    return response.status_code