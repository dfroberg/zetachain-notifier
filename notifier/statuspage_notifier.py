import requests
from loguru import logger

def format_status_for_statuspage(update, customer):
    return (
        f"Hi {customer['name']}\n\n"
        f"*Status Update: {update['title']}*\n"
        f"{update['latest_update']}\n\n"
        f"Status: {update['status']}\n"
        f"Impact: {update['impact']}\n"
        f"Link: {update['link']}\n"
    )

def format_governance_for_statuspage(proposal, customer):
    tags_text = ", ".join([f"`{tag}`" for tag in customer["groups"]])
    return (
        f"Hi {customer['name']}\n\n"
        f"{proposal['status_icon']} *Governance Proposal: #{proposal['id']} - {proposal['title']}*\n"
        f"{proposal['summary']}\n\n"
        f"Status: {proposal['status']}\n"
        f"Type: {proposal['type']}\n"
        f"Submit Time: {proposal['submit_time']}\n"
        f"Deposit End Time: {proposal['deposit_end_time']}\n"
        f"Voting End Time: {proposal['voting_end_time']}\n"
        "Votes Tallies:\n"
        f"Yes\n{proposal['yes_percentage']:.2f}%\n{proposal['yes_count']:,.2f} ZETA\n\n"
        f"No\n{proposal['no_percentage']:.2f}%\n{proposal['no_count']:,.2f} ZETA\n\n"
        f"Abstain\n{proposal['abstain_percentage']:.2f}%\n{proposal['abstain_count']:,.2f} ZETA\n\n"
        f"No with Veto\n{proposal['no_with_veto_percentage']:.2f}%\n{proposal['no_with_veto_count']:,.2f} ZETA\n"
        f"More details: {proposal['proposal_link']}\n"
        f"Sent via Zetachain Community Notifier\n"
        f"Tags: {tags_text}"
    )

def update_statuspage(api_key, page_id, message):
    url = f"https://api.statuspage.io/v1/pages/{page_id}/incidents"
    headers = {"Authorization": f"OAuth {api_key}"}
    data = {"incident": {"name": "Update", "status": "investigating", "body": message}}
    response = requests.post(url, headers=headers, json=data)
    logger.info(f"Updated Statuspage with status code {response.status_code}")
    return response.status_code