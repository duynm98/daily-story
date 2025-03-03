import os
import sys
import yaml

from dotenv import load_dotenv
from loguru import logger

logger.remove()
logger.add(
    sys.stderr,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SS}</green> | <level>{level: <8}</level> | <black>{name}:{line}</black> - <level>{message}</level>",
)
logger.level("INFO", color="<blue>")
logger.level("DEBUG", color="<magenta>")

# logger.info("info")
# logger.debug("debug")
# logger.error("error")
# logger.warning("warning")
# logger.critical("critical")

logger.info("Loading environment variables...")
load_dotenv()


def load_config(config_file: str = "config.yaml"):
    if not os.path.exists(config_file):
        logger.error(f"Config file does not exists: {config_file}")
        return None

    with open(config_file) as f:
        return yaml.safe_load(f)


config = load_config()
