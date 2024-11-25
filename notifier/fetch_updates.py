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
        updates = response.json()

        # Fetch components and update tags
        components = fetch_statuspage_components(api_key, page_id)
        for update in updates:
            affected_components = [component["name"] for component in components if component["status"] != "operational"]
            if affected_components:
                update["tags"] = affected_components
            else:
                update["tags"] = ["all", "any"]

        return updates
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

def fetch_governance_proposals(network):
    url = network["endpoint"]
    headers = {'accept': 'application/json'}
    
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504, 522, 524])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    
    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()
        logger.info(f"Fetched governance proposals for {network['name']}")
        proposals = response.json().get('proposals', [])
        for proposal in proposals:
            proposal['tags'] = [network['name']]
        return proposals
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch governance proposals for {network['name']}: {e}")
        return []

def fetch_broadcast(proposal_id=None):
    proposals = fetch_governance_proposals()
    if proposal_id:
        for proposal in proposals:
            if proposal['id'] == proposal_id:
                return proposal
    return None