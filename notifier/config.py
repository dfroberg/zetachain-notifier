import os
import yaml
from loguru import logger

CONFIG_FILE = 'config.yaml'

def load_config():
    with open(CONFIG_FILE, 'r') as file:
        config = yaml.safe_load(file)
    return config

def get_config_mtime():
    return os.path.getmtime(CONFIG_FILE)

def check_config_update(config_mtime):
    current_mtime = get_config_mtime()
    if current_mtime != config_mtime:
        logger.info("Detected changes in config.yaml, reloading configuration")
        new_config = load_config()
        return new_config, current_mtime
    return None, config_mtime

config = load_config()
config_mtime = get_config_mtime()
avatar_url = config['avatar_url']
statuspages = config['statuspages']
customers = config['customers']

logger.info("Loaded configuration")