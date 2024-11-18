import os
import pickle
import hashlib
from datetime import datetime
from dateutil.parser import isoparse, ParserError
import dateparser
from loguru import logger

PICKLE_FILE = 'sent_updates.pkl'
COMPONENTS_FILE = 'affected_components.pkl'

def parse_date(date_str, incident_or_proposal_id, date_type):
    logger.debug(f"Raw {date_type} date for ID {incident_or_proposal_id}: {date_str}")
    try:
        logger.debug(f"Attempting ISO 8601 parse for {date_type} date: {date_str}")
        return isoparse(date_str)
    except (ParserError, ValueError):
        logger.debug(f"Attempting relative time parse for {date_type} date: {date_str}")
        parsed_date = dateparser.parse(date_str)
        if parsed_date:
            return parsed_date
        else:
            logger.error(f"Failed to parse {date_type} date for ID {incident_or_proposal_id}: {date_str}")
            return date_str

def hash_data(data):
    data_copy = data.copy()
    for key in list(data_copy.keys()):
        if key.endswith('_display'):
            del data_copy[key]
    data_str = str(data_copy)
    logger.debug(f"Hashing data: {data_str}")
    return hashlib.md5(data_str.encode('utf-8')).hexdigest()

def load_sent_updates():
    if os.path.exists(PICKLE_FILE):
        with open(PICKLE_FILE, 'rb') as f:
            logger.info("Loaded sent updates from pickle file")
            return pickle.load(f)
    logger.info("No sent updates found, returning empty set")
    return set()

def save_sent_updates(sent_updates):
    with open(PICKLE_FILE, 'wb') as f:
        pickle.dump(sent_updates, f)
    logger.info("Saved sent updates to pickle file")

def load_affected_components():
    if os.path.exists(COMPONENTS_FILE):
        with open(COMPONENTS_FILE, 'rb') as f:
            logger.info("Loaded affected components from pickle file")
            return pickle.load(f)
    logger.info("No affected components found, returning empty dict")
    return {}

def save_affected_components(affected_components):
    with open(COMPONENTS_FILE, 'wb') as f:
        pickle.dump(affected_components, f)
    logger.info("Saved affected components to pickle file")