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

required_config = ["video"]


def load_config():
    if not os.path.exists(CONFIG_FILE):
        logger.error(f"Config file does not exists: {CONFIG_FILE}")
        return None

    with open(CONFIG_FILE) as f:
        config = yaml.safe_load(f)

        # Validate config
        for k in required_config:
            if k not in config:
                logger.error(f"Config missing: {k}")
                raise ValueError(f"Config missing: {k}")

        _font_path = config["video"]["font_path"]
        if not os.path.exists(_font_path):
            logger.error(f"Font path: {_font_path} does not exists.")
            raise ValueError(f"Font path: {_font_path} does not exists.")

        _font_size = config["video"]["font_size"]
        if not isinstance(_font_size, int) or _font_size <= 0:
            logger.error("Font size must be a positive integer")
            raise ValueError("Font size must be a positive integer")
        if _font_size < 20:
            logger.warning(f"Font size {_font_size} might be too small!")

        _language = config["video"]["language"]
        if not _language.lower().strip() in ["vietnamese", "english"]:
            logger.error(f"Language must be either 'Vietnamese' or 'English'. Got: '{_language}'. Please check your settings")
            raise ValueError(f"Language must be either 'Vietnamese' or 'English'. Got: '{_language}'. Please check your settings")

        logger.success(f"Succesfully loaded config from {CONFIG_FILE}")
        logger.info(f"Config:\n{config}")

        return config


def save_config(new_config: dict):
    with open(CONFIG_FILE, "w") as file:
        yaml.dump(new_config, file, default_flow_style=False, allow_unicode=True)

    global config
    config = load_config()


config = load_config()
