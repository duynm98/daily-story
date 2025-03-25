import os
import glob
import shutil
from uuid import uuid4
import datetime

from loguru import logger

from app import config
from app.core.story import fetch_random_vi_story, fetch_short_story, fetch_all_available_morals, fetch_all_stories
from app.core.images import get_images, image2video
from app.core.voice import create_voice_and_subtitle
from app.core.video import generate_video, combine_videos
from app.core.llm import generate_terms, translate_to_vietnamese, generate_story_from_moral
from app.core.models.schema import VideoParams

_max_retries = 3


_voice_rate = config["video"].get("voice_rate", 1.0)
_language = config["video"].get("language", "English").lower().strip()


def generate_video_from_moral(moral: str) -> str:
    task_id = datetime.now().strftime("%Y_%m_%d_%H_%M")
    if not moral:
        logger.error("moral cannot be empty")
        return ""

    if _language == "vietnamese":
        moral = translate_to_vietnamese(moral)

    story = {"moral": moral, "story": generate_story_from_moral(moral)}
    if not story["story"]:
        logger.error(f"Failed to generate story from moral '{moral}'")
        return ""

    # Create a temp folder to store the resources
    output_folder = os.path.join("temp", task_id)
    os.makedirs(output_folder, exist_ok=True)

    # Retrieve search terms if exist:
    for attemp in range(_max_retries):
        try:
            logger.info(f"Creating a video from moral. Try {attemp}")

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
            voice_name = "en-US-AndrewNeural-Male" if _language == "english" else "vi-VN-NamMinhNeural"
            subtitle_output_file, audio_duration = create_voice_and_subtitle(
                voice_name=voice_name,
                text=story["moral"] + "\n" + story["story"],
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
                video_path=video_path,
                audio_path=audio_path,
                subtitle_path=subtitle_output_file,
                output_file=final_video_path,
                params=VideoParams(),
            )

            logger.success(f"Task {task_id} completed!")

            # shutil.rmtree(output_folder, ignore_errors=True)
            # logger.info(f"All files in {output_folder} have been deleted")

            return final_video_path

        except Exception as e:
            logger.error(f"Something wrong when execute task {task_id}: {e}. Trying again")
            continue

    logger.error(f"Failed to execute task {task_id}.")
    return ""
