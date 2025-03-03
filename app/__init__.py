import os
import sys
import yaml

from dotenv import load_dotenv
from loguru import logger

logger.remove()
logger.add(
    sys.stderr,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SS}</green> | <level>{level: <8}</level> | <cyan>{name}:{line}</cyan> - <level>{message}</level>",
)
logger.level("INFO", color="<blue>")
logger.level("DEBUG", color="<magenta>")

logger.info("Loading environment variables...")
load_dotenv()

CONFIG_FILE = "config.yaml"


def load_config():
    if not os.path.exists(CONFIG_FILE):
        logger.error(f"Config file does not exists: {CONFIG_FILE}")
        return None

    with open(CONFIG_FILE) as f:
        config = yaml.safe_load(f)
        logger.success(f"Succesfully loaded config from {CONFIG_FILE}")
        logger.info(f"Config:\n{config}")
        return config


def save_config(new_config: dict):
    with open(CONFIG_FILE, "w") as file:
        yaml.dump(new_config, file, default_flow_style=False, allow_unicode=True)

    global config
    config = load_config()


config = load_config()
