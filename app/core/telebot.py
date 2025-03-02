import os

import telepot
from loguru import logger

from app import config

_tele_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
if not _tele_bot_token:
    _tele_bot_token = config["telegram"].get("bot_token", "")

_tele_chat_id = os.getenv("TELEGRAM_CHAT_ID")
if not _tele_chat_id:
    _tele_chat_id = config["telegram"].get("chat_id", "")

bot = telepot.Bot(_tele_bot_token) if _tele_bot_token else None


def send_message(message: str):
    if bot is None or not _tele_chat_id:
        return

    try:
        bot.sendMessage(chat_id=_tele_chat_id, text=message)
        logger.info("Message sent to Telegram")
    except Exception as e:
        logger.error(f"Cannot send message to Telegram: {e}")


def send_video(video_path: str, caption: str):
    if bot is None or not _tele_chat_id:
        return

    logger.info(f"Sending video {video_path} to Telegram. Caption: {caption}")
    try:
        bot.sendVideo(chat_id=_tele_chat_id, video=open(video_path, "rb"), caption=caption)
        logger.success(f"Video {os.path.basename(video_path)} sent to Telegram")
    except Exception as e:
        logger.error(f"Cannot send video to Telegram {e}")


if __name__ == "__main__":
    bot_update = bot.getUpdates()
    send_message("Hello from code")
    # import rich; from rich import inspect; from rich import print as rprint; import ipdb; ipdb.set_trace()
