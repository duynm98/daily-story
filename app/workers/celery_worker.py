import json
import os

from dotenv import load_dotenv
from celery import Celery, Task

# from app.workers.celery_tasks import GenerateStory, GenerateVideo
from app.core.generator import generate_video_from_moral
from app.core.llm import generate_story_from_moral

RESULT_EXPIRE_TIME = 60 * 60 * 10  # keep tasks around for ten hours

load_dotenv()

app = Celery(
    "daily-story",
    broker_url=os.environ.get("CELERY_BROKER_URL"),
    backend_url=os.environ.get("CELERY_RESULT_BACKEND"),
    # result_expires=RESULT_EXPIRE_TIME,
)


app.conf.update(
    enable_utc=True,
    timezone="Asia/Saigon",
    broker_connection_retry_on_startup=True,
)

app.autodiscover_tasks()


@app.task(name="generate-story", bind=True)
def generate_story(self, moral: str):
    return generate_story_from_moral(moral)


@app.task(name="generate-video", bind=True)
def generate_video(self, moral: str, task_id: str):
    return generate_video_from_moral(moral, task_id)
