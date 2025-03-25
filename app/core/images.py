import os
import requests
import urllib.parse
import json
from rich.progress import track
import math
import random

import cv2
import numpy as np
from loguru import logger

# Replace with your actual API key

# Replace with your actual API key
API_KEY = os.getenv("PEXELS_API_KEY")
BASE_URL = "https://api.pexels.com/v1/search"


def get_images(query: str, output_folder: str, orientation: str = "portrait", amount: int = 5) -> list:
    """Fetches images from Pexels API and saves them to the output folder.

    Args:
        query (str): The search term for images.
        output_folder (str): Directory to save downloaded images.
        orientation (str, optional): Image orientation ('portrait', 'landscape', etc.). Defaults to "portrait".
        amount (int, optional): Number of images to fetch. Defaults to 5.

    Returns:
        list: A list of saved image file paths.
    """
    logger.info(f"\n\n## Fetching images from Pexels\n## query: '{query}'\n## amount: {amount}\n## orientation: {orientation}")
    os.makedirs(output_folder, exist_ok=True)

    # Encode the query to be URL-safe
    encoded_query = urllib.parse.quote(query)
    url = f"{BASE_URL}?query={encoded_query}&orientation={orientation}&per_page={min(amount, 5)}"

    headers = {"Authorization": API_KEY}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        logger.info("Fetching images successfully.")

        data = response.json()
        photos = data.get("photos", [])
        logger.info(f"Saving {len(photos)} images to {output_folder}")

        saved_files = []
        for idx, photo in enumerate(photos):
            photo_url = photo["src"]["original"]
            photo_id = photo.get("id", f"NoID_{idx}")

            img_response = requests.get(photo_url)
            img_response.raise_for_status()  # Check if the image was retrieved successfully

            filename = os.path.join(output_folder, f"{photo_id}.jpg")

            with open(filename, "wb") as f:
                f.write(img_response.content)

            saved_files.append(filename)

        logger.info(f"Successfully downloaded {len(saved_files)} images to {output_folder}")
        if len(saved_files) > amount:
            saved_files = random.choices(saved_files, k=amount)
        return saved_files

    except requests.RequestException as e:
        logger.error(f"Error fetching images: {e}")
        return []


def image2video(image_path: str, output_video_path: str, duration: float):
    max_attemp = 3
    while max_attemp > 0:
        try:
            logger.info(f"Generating video from image: {image_path}")

            # Load the image
            image = cv2.imread(image_path)

            black = np.zeros_like(image, dtype=np.uint8)
            image = cv2.addWeighted(image, 0.6, black, 0.4, 0.0)
            # brightness_reduction = 20
            # image = cv2.subtract(image, np.full(image.shape, brightness_reduction, dtype=np.uint8))

            # Define video resolution (1080x1920)
            video_width, video_height = 1080, 1920
            fps = 25  # Frames per second
            num_frames = math.ceil(fps * duration)

            # Resize image while maintaining aspect ratio (fill 1080x1920)
            img_height, img_width = image.shape[:2]
            if img_width / img_height < 9 / 16:
                logger.warning(f"The image size is {img_width} x {img_height} may cause the video looks unusual")

            scale = max(video_width / img_width, video_height / img_height)  # Scale to cover
            new_width, new_height = int(img_width * scale), int(img_height * scale)
            resized_image = cv2.resize(image, (new_width, new_height))

            # Video writer
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(output_video_path, fourcc, fps, (video_width, video_height))

            diff = min(720, max(new_width - video_width, new_height - video_height))
            # diff = new_width - video_width - 1
            x_crop_start = max(0, (new_width - video_width - diff) // 2 - 1)
            y_crop_start = 0

            # print(new_width, video_width, diff)
            # print(x_crop_start, y_crop_start)

            # Translation settings
            max_translation = diff  # Maximum translation in pixels

            for i in track(range(num_frames), description="Generating video"):
                # Compute translation offsets (move horizontally and vertically)
                tx = int((max_translation * i) / num_frames)  # Move in x direction
                ty = int((max_translation * i) / num_frames)  # Move in y direction

                # Ensure image stays within bounds
                x_pos = min(max(x_crop_start + tx, 0), new_width - video_width)
                y_pos = min(max(y_crop_start + ty, 0), new_height - video_height)

                # Crop translated frame from resized image
                frame = resized_image[y_pos : y_pos + video_height, x_pos : x_pos + video_width]

                # Write frame to video
                out.write(frame)

            # Release video writer
            out.release()
            logger.info(f"Video saved as {output_video_path}")
            return
        except Exception as e:
            logger.warning(f"Cannot generate video from image {image_path}. Attemp again")
            max_attemp -= 1

    logger.error(f"Generate video from image {image_path} failed!")


# Example usage
if __name__ == "__main__":
    # images = get_images("Why did the designer break up with their font?", "./temp")
    # print("Downloaded files:", images)

    image2video("/Users/duynm/duynm/me/playground/daily-space-news/assets/images/Space matters.jpeg", "test.mp4", duration=5)
