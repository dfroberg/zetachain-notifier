import textwrap
import requests
from loguru import logger

"""
This module is intended to be used as a notifier for Statuspage updates for customers 
with their own Statuspage, to indicate that there are issues with the service due to 
Zetachain issues. This is useful for customers who rely on Zetachain services and want
to keep their users informed about any potential issues.
"""

def format_status_for_statuspage(update, customer, config):
    # log the entire update for debugging purposes
    logger.debug(f"Status update: {update}")
    return ({
            "incident": 
            {
                "name": f"Upstream Issue:  {update['title']}", 
                "status": update['status'], # 'investigating', 'resolved', 'under investigation', 'new'
                "body": textwrap.dedent(f"""
                    {update['latest_update']}
                    
                    *Status:* {update['status']}
                    *Impact:* {update['impact']}
                    *Link:* {update['link']}
                """)
            }
            })

def update_statuspage(api_key, page_id, message, config):
    url = f"https://api.statuspage.io/v1/pages/{page_id}/incidents"
    headers = {"Authorization": f"OAuth {api_key}"}
    data = message
    response = requests.post(url, headers=headers, json=data)
    logger.info(f"Updated Statuspage with status code {response.status_code}")
    return response.status_code