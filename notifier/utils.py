import hashlib
import os
import jsonpickle
from datetime import datetime, timedelta
from dateutil.parser import isoparse, ParserError
import dateparser
from loguru import logger

PICKLE_FILE = 'sent_updates.json'
COMPONENTS_FILE = 'affected_components.json'

def parse_timestamp(timestamp):
    try:
        # Try parsing with fractional seconds
        return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        # Fallback to parsing without fractional seconds
        return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")

def parse_date(date_str, incident_or_proposal_id, date_type):
    #logger.debug(f"Raw {date_type} date for ID {incident_or_proposal_id}: {date_str}")
    try:
        #logger.debug(f"Attempting ISO 8601 parse for {date_type} date: {date_str}")
        return isoparse(date_str)
    except (ParserError, ValueError):
        #logger.debug(f"Attempting relative time parse for {date_type} date: {date_str}")
        parsed_date = dateparser.parse(date_str)
        if parsed_date:
            return parsed_date
        else:
            logger.error(f"Failed to parse {date_type} date for ID {incident_or_proposal_id}: {date_str}")
            return date_str

def hash_data(data):
    if isinstance(data, str):
        data_str = data
    elif isinstance(data, dict):
        data_copy = data.copy()
        # Remove _display fields
        for key in list(data_copy.keys()):
            if key.endswith('_display'):
                del data_copy[key]
        data_str = str(data_copy)
    elif isinstance(data, list):
        # Convert list to a string representation
        data_str = str(data)
    else:
        # Handle other types if necessary
        data_str = str(data)
    
    #logger.debug(f"Hashing data: {data_str}")
    return hashlib.md5(data_str.encode('utf-8')).hexdigest()

def load_sent_updates():
    if os.path.exists(PICKLE_FILE):
        with open(PICKLE_FILE, 'r') as f:
            logger.info("Loaded sent updates from JSON file")
            return set(jsonpickle.decode(f.read()))
    logger.info("No sent updates found, returning empty set")
    return set()

def save_sent_updates(sent_updates):
    with open(PICKLE_FILE, 'w') as f:
        f.write(jsonpickle.encode(list(sent_updates)))
    logger.info("Saved sent updates to JSON file")

def load_affected_components():
    if os.path.exists(COMPONENTS_FILE):
        with open(COMPONENTS_FILE, 'r') as f:
            logger.info("Loaded affected components from JSON file")
            return jsonpickle.decode(f.read())
    logger.info("No affected components found, returning empty dict")
    return {}

def save_affected_components(affected_components):
    with open(COMPONENTS_FILE, 'w') as f:
        f.write(jsonpickle.encode(affected_components))
    logger.info("Saved affected components to JSON file")

def match_customers_to_update(update, customers):
    affected_customers = []
    update_tags = set(update.get("tags", ["any", "all"]))
    for customer in customers:
        customer_tags = set(customer.get("groups", []))
        if "any" in customer_tags or "all" in customer_tags or customer_tags & update_tags:
            affected_customers.append(customer)
            logger.debug(f"Matched customer {customer['name']} to update {update['id']}") if customer["enable"] else logger.debug(f"Matched customer {customer['name']} to update {update['id']} (disabled)")
        else:
            logger.debug(f"Did not match customer {customer['name']} to update {update['id']}") if customer["enable"] else logger.debug(f"Did not match customer {customer['name']} to update {update['id']} (disabled)")
            logger.debug(f"Customer tags: {customer_tags}")
            logger.debug(f"Update tags: {update_tags}") if update_tags else logger.debug(f"Update tags: None")
    return affected_customers

def get_color_based_on_status(status,type = "int"):
    # Statuspage statuses
    if status == 'investigating':
        color = 0xffa500  # Orange color
    elif status == 'resolved':
        color = 0x00ff00  # Green color
    elif status == 'under investigation':
        color = 0xffff00  # Yellow color
    elif status == 'identified':
        color = 0xFF8C00  # Dark Orange color
    elif status == 'new':
        color = 0x0000ff  # Blue color
    elif status == 'postmortem':
        color = 0x800080  # Purple color
    elif status == 'scheduled':
        color = 0x808080  # Gray color
    elif status == 'monitoring':
        color = 0x90EE90  # Light green color
    # Governance proposal statuses
    elif status == 'PROPOSAL_STATUS_REJECTED':
        color = 0xff0000  # Red color
    elif status == 'PROPOSAL_STATUS_ACCEPTED':
        color = 0x00ff00  # Green color
    elif status == 'PROPOSAL_STATUS_UNSPECIFIED':
        color = 0xffff00  # Yellow color
    # Default color
    else:
        color = 0x000000  # Black color
    if type == "hex_string":
        return f"#{color:06x}"
    else:
        return color
    