import os
import yaml

from dotenv import load_dotenv
from loguru import logger

logger.info("Loading environment variables...")
load_dotenv()


def load_config(config_file: str = "config.yaml"):
    if not os.path.exists(config_file):
        logger.error(f"Config file does not exists: {config_file}")
        return None

    with open(config_file) as f:
        return yaml.safe_load(f)


config = load_config()
