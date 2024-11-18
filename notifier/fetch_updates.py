import requests
from loguru import logger
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def fetch_status_updates(api_key, page_id):
    url = f"https://api.statuspage.io/v1/pages/{page_id}/incidents"
    headers = {"Authorization": f"OAuth {api_key}"}
    
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504, 522, 524])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    
    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()
        logger.info("Fetched status updates")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch status updates: {e}")
        return []

def fetch_statuspage_components(api_key, page_id):
    url = f"https://api.statuspage.io/v1/pages/{page_id}/components"
    headers = {"Authorization": f"OAuth {api_key}"}
    
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504, 522, 524])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    
    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()
        logger.info(f"Fetched components for status page {page_id}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch components for status page {page_id}: {e}")
        return []

def fetch_governance_proposals():
    url = 'https://zetachain.blockpi.network/lcd/v1/public/cosmos/gov/v1/proposals?proposal_status=PROPOSAL_STATUS_UNSPECIFIED&pagination.count_total=true&pagination.reverse=true'
    headers = {'accept': 'application/json'}
    
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504, 522, 524])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    
    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()
        logger.info("Fetched governance proposals")
        return response.json().get('proposals', [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch governance proposals: {e}")
        return []

def fetch_broadcast(proposal_id=None):
    proposals = fetch_governance_proposals()
    if proposal_id:
        for proposal in proposals:
            if proposal['id'] == proposal_id:
                return proposal
    return None