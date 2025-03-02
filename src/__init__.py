import yaml

from dotenv import load_dotenv
from loguru import logger

logger.info("Loading environment variables...")
load_dotenv()


def load_config(config_file: str = "config.yaml"):
    with open(config_file) as f:
        return yaml.safe_load(f)


config = load_config()
