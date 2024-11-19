import textwrap
import humanize
from utils import parse_date
from loguru import logger

def format_status_update(incident):
    latest_update = incident["incident_updates"][0] if incident["incident_updates"] else {}
    created_at = incident["created_at"]
    updated_at = incident["updated_at"]
    resolved_at = incident.get("resolved_at")

    created_at_display = humanize.naturaltime(parse_date(created_at, incident["id"], "created_at"))
    updated_at_display = humanize.naturaltime(parse_date(updated_at, incident["id"], "updated_at"))
    resolved_at_display = humanize.naturaltime(parse_date(resolved_at, incident["id"], "resolved_at")) if resolved_at else None

    formatted_update = {
        "id": incident["id"],
        "title": incident["name"],
        "link": incident["shortlink"],
        "status": incident["status"],
        "created_at": created_at,
        "created_at_display": created_at_display,
        "updated_at": updated_at,
        "updated_at_display": updated_at_display,
        "resolved_at": resolved_at,
        "resolved_at_display": resolved_at_display,
        "impact": incident["impact"],
        "latest_update": latest_update.get('body', 'No updates available.'),
        "tags": incident.get('tags', [])
    }
    return formatted_update

def format_governance_proposal(proposal):
    proposal_link = f"https://hub.zetachain.com/governance/proposal/{proposal['id']}"
    status_icon = {
        "PROPOSAL_STATUS_REJECTED": ":x:",
        "PROPOSAL_STATUS_PASSED": ":white_check_mark:",
        "PROPOSAL_STATUS_UNSPECIFIED": ":grey_question:"
    }.get(proposal["status"], ":grey_question:")
    
    final_tally_result = proposal.get("final_tally_result", {})
    yes_count = int(final_tally_result.get("yes_count", "0")) / 1e6
    abstain_count = int(final_tally_result.get("abstain_count", "0")) / 1e6
    no_count = int(final_tally_result.get("no_count", "0")) / 1e6
    no_with_veto_count = int(final_tally_result.get("no_with_veto_count", "0")) / 1e6
    total_votes = yes_count + abstain_count + no_count + no_with_veto_count

    def safe_percentage(count, total):
        return (count / total) * 100 if total > 0 else 0

    yes_percentage = safe_percentage(yes_count, total_votes)
    abstain_percentage = safe_percentage(abstain_count, total_votes)
    no_percentage = safe_percentage(no_count, total_votes)
    no_with_veto_percentage = safe_percentage(no_with_veto_count, total_votes)

    submit_time = parse_date(proposal['submit_time'], proposal['id'], "submit_time")
    deposit_end_time = parse_date(proposal['deposit_end_time'], proposal['id'], "deposit_end_time")
    voting_end_time = parse_date(proposal['voting_end_time'], proposal['id'], "voting_end_time")

    submit_time_display = humanize.naturaltime(submit_time)
    deposit_end_time_display = humanize.naturaltime(deposit_end_time)
    voting_end_time_display = humanize.naturaltime(voting_end_time)

    formatted_proposal = {
        "status_icon": status_icon,
        "id": proposal['id'],
        "title": proposal['title'],
        "summary": proposal['summary'],
        "status": proposal['status'],
        "type": proposal['messages'][0]['@type'],
        "submit_time": submit_time,
        "submit_time_display": submit_time_display,
        "deposit_end_time": deposit_end_time,
        "deposit_end_time_display": deposit_end_time_display,
        "voting_end_time": voting_end_time,
        "voting_end_time_display": voting_end_time_display,
        "yes_count": yes_count,
        "abstain_count": abstain_count,
        "no_count": no_count,
        "no_with_veto_count": no_with_veto_count,
        "yes_percentage": yes_percentage,
        "abstain_percentage": abstain_percentage,
        "no_percentage": no_percentage,
        "no_with_veto_percentage": no_with_veto_percentage,
        "proposal_link": proposal_link
    }
    return formatted_proposal

def format_broadcast_for_discord(message, customer, config):
    avatar_url = config['avatar_url']
    embed = {
        "author": {
            "name": "Zetachain Community Notifier",
            "icon_url": avatar_url
        },
        "status": "new",
        "description": message,
        "color": 0x0000ff,  # Blue color for broadcast
        "footer": {
            "text": f"Sent via Zetachain Community Notifier\nTags: {', '.join([f'`{tag}`' for tag in customer['groups']])}"
        }
    }
    return embed

def format_broadcast_for_slack(message, customer, config):
    tags_text = ", ".join([f"`{tag}`" for tag in customer["groups"]])
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Hi {customer['name']}\n\n{message}"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Sent via Zetachain Community Notifier\n\nTags: {tags_text}"
                }
            ]
        },
        {
            "type": "divider"
        }
    ]

def format_broadcast_for_telegram(message, customer, config):
    tags_text = ", ".join([f"`{tag}`" for tag in customer["groups"]])
    return textwrap.dedent(f"""
        Hi {customer['name']}

        {message}

        _Sent via Zetachain Community Notifier_
        Tags: {tags_text}
    """)

def format_governance_broadcast_for_discord(message, proposal, customer, config):
    avatar_url = config['avatar_url']
    embed = {
        "author": {
            "name": "Zetachain Community Notifier",
            "icon_url": avatar_url
        },
        "title": f"{proposal['status_icon']} Governance Proposal: #{proposal['id']} - {proposal['title']}",
        "description": f"{message}\n\n**Description:**\n{proposal['summary']}",
        "color": 0x0000ff,  # Blue color for broadcast
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

def format_governance_broadcast_for_slack(message, proposal, customer, config):
    tags_text = ", ".join([f"`{tag}`" for tag in customer["groups"]])
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Hi {customer['name']}\n\n{message}\n\n*Governance Proposal: #{proposal['id']} - {proposal['title']}*\n{proposal['summary']}"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Status:*\n{proposal['status']}"},
                {"type": "mrkdwn", "text": f"*Type:*\n{proposal['type']}"},
                {"type": "mrkdwn", "text": f"*Submit Time:*\n{proposal['submit_time_display']}"},
                {"type": "mrkdwn", "text": f"*Deposit End Time:*\n{proposal['deposit_end_time_display']}"},
                {"type": "mrkdwn", "text": f"*Voting End Time:*\n{proposal['voting_end_time_display']}"},
                {"type": "mrkdwn", "text": f"*Yes:*\n{proposal['yes_percentage']:.2f}%\n{proposal['yes_count']:,.2f} ZETA"},
                {"type": "mrkdwn", "text": f"*No:*\n{proposal['no_percentage']:.2f}%\n{proposal['no_count']:,.2f} ZETA"},
                {"type": "mrkdwn", "text": f"*Abstain:*\n{proposal['abstain_percentage']:.2f}%\n{proposal['abstain_count']:,.2f} ZETA"},
                {"type": "mrkdwn", "text": f"*No with Veto:*\n{proposal['no_with_veto_percentage']:.2f}%\n{proposal['no_with_veto_count']:,.2f} ZETA"}
            ]
        },
        {
            "type": "divider"
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"More details: {proposal['proposal_link']}"
                }
            ]
        },
        {
            "type": "divider"
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Sent via Zetachain Community Notifier\n\nTags: {tags_text}"
                }
            ]
        },
        {
            "type": "divider"
        }
    ]

def format_governance_broadcast_for_telegram(message, proposal, customer, config):
    tags_text = ", ".join([f"`{tag}`" for tag in customer["groups"]])
    return textwrap.dedent(f"""
        Hi {customer['name']}

        {message}

        *Governance Proposal: #{proposal['id']} - {proposal['title']}*
        {proposal['summary']}

        *Status:* {proposal['status']}
        *Type:* {proposal['type']}
        *Submit Time:* {proposal['submit_time_display']}
        *Deposit End Time:* {proposal['deposit_end_time_display']}
        *Voting End Time:* {proposal['voting_end_time_display']}
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

        _Sent via Zetachain Community Notifier_
        Tags: {tags_text}
    """)