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

config = load_config()
config_mtime = get_config_mtime()
avatar_url = config['avatar_url']
statuspages = config['statuspages']
customers = config['customers']

logger.info("Loaded configuration")