import requests
import random
import json

import pandas as pd
from loguru import logger

API_URL = "https://shortstories-api.onrender.com"

ORG_STORIES = "data/stories.json"
ALL_MORALS = "data/morals.json"
VI_STORIES = "data/vi_stories_1_700.csv"

_max_retries = 5


def fetch_short_story() -> dict:
    """Fetch a short story from the API and return the JSON response."""
    i = 1
    while i < _max_retries:
        try:
            response = requests.get(API_URL, timeout=5)
            response.raise_for_status()  # Raise an error for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            i + 1
            logger.error(f"Failed to fetch data: {e}. Trying again #{i}")
            return None


def fetch_random_vi_story() -> dict:
    max_attemp = 3
    while max_attemp > 0:
        try:
            df = pd.read_csv(VI_STORIES)
            data = df.to_dict(orient="records")
            story = random.choice(data)

            logger.info(f"A story was fetched: id: {story['_id']}")
            return story

        except Exception as e:
            if max_attemp > 0:
                logger.error(f"Cannot fetch story: {e}. Try again")
                max_attemp -= 1
            else:
                logger.error(f"Fetch story failed!")
                return None


def fetch_all_stories():
    try:
        with open(ORG_STORIES) as f:
            return json.load(f)
    except Exception as e:
        response = requests.get(f"{API_URL}/stories")
        return response.json()


def fetch_all_available_morals():
    try:
        with open(ALL_MORALS) as f:
            morals = json.load(f)
            morals = {k: v for k, v in morals.items() if v}
            return morals
    except Exception as e:
        logger.warning("Cannot fetch morals")
        return {}


if __name__ == "__main__":
    story = fetch_random_vi_story()
    # fetch_all_stories()
    # story = fetch_short_story()
    # if story:
    #     logger.info("Fetched story successfully:")
    #     print(story)
    # else:
    #     logger.warning("No story retrieved.")
