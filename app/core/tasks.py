import os
import glob
import shutil
from uuid import uuid4
import random

from loguru import logger

from app import config
from app.core.story import fetch_random_vi_story, fetch_short_story, fetch_all_available_morals, fetch_all_stories
from app.core.images import get_images, image2video
from app.core.voice import create_voice_and_subtitle
from app.core.video import generate_video, combine_videos
from app.core.llm import generate_terms, translate_to_vietnamese, generate_story_from_moral
from app.core.models.schema import VideoParams
from app.core import telebot

_max_retries = 3


_output_folder = config["app"].get("output_folder", "./output")
_voice_rate = config["video"].get("voice_rate", 1.0)


def init_task() -> str:
    task_id = str(uuid4())
    os.makedirs(os.path.join(_output_folder, task_id), exist_ok=True)
    logger.info(f"Successfully init task: {task_id}")
    return task_id


def execute_task(task_id: str, delete_on_complete: bool = False):
    for attemp in range(_max_retries):
        try:
            logger.info(f"Executing task {task_id}. Attemp {attemp}")

            output_folder = os.path.join(_output_folder, task_id)

            # Fetch a random story
            en2vi_morals = fetch_all_available_morals()
            stories = fetch_all_stories()
            story = random.choice([s for s in stories if s["moral"] in en2vi_morals])

            story["story"] = generate_story_from_moral(story["moral"], story["story"])
            story["moral"] = en2vi_morals[story["moral"]]

            assert story["moral"] and story["story"]

            # Retrieve search terms if exist:
            search_terms = story.get("search_terms", [])
            if not search_terms:
                search_terms = generate_terms(content=story["story"], amount=5)

            images_folder = os.path.join(output_folder, "images")
            os.makedirs(images_folder, exist_ok=True)
            images = []
            for search_term in search_terms:
                images += get_images(query=search_term, output_folder=images_folder, amount=1)

            assert len(images) > 0, "No images found"

            audio_path = os.path.join(output_folder, "audio.mp3")
            subtitle_output_file, audio_duration = create_voice_and_subtitle(
                voice_name="vi-VN-NamMinhNeural",
                text=story["moral"] + "\n" + story["story"] + "\nVì vậy, hãy nhớ rằng:",
                voice_output_file=audio_path,
                voice_rate=_voice_rate,
            )

            output_video_folder = os.path.join(output_folder, "videos")
            os.makedirs(output_video_folder, exist_ok=True)
            for image_path in images:
                video_path = os.path.join(output_video_folder, f"video-{os.path.basename(image_path)}.mp4")
                image2video(image_path, video_path, audio_duration / len(images))

            video_path = combine_videos(
                os.path.join(output_folder, "video.mp4"),
                glob.glob(os.path.join(output_video_folder, "*")),
                audio_path,
                max_clip_duration=audio_duration / len(images),
            )

            final_video_path = os.path.join(output_folder, "video-final.mp4")
            generate_video(
                video_path=video_path, audio_path=audio_path, subtitle_path=subtitle_output_file, output_file=final_video_path, params=VideoParams()
            )

            logger.success(f"Task {task_id} completed!")

            telebot.send_message(f"Bài học cuộc sống: {story['moral']}\n{story['story']}")
            telebot.send_video(final_video_path, caption=task_id)

            if delete_on_complete:
                shutil.rmtree(output_folder, ignore_errors=True)
                logger.info(f"All files in {output_folder} have been deleted")

            return

        except Exception as e:
            logger.error(f"Something wrong when execute task {task_id}. Trying again")
            continue

    logger.error(f"Failed to execute task {task_id}.")


if __name__ == "__main__":
    task_id = init_task()
    execute_task(task_id, delete_on_complete=False)
