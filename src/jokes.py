from loguru import logger
import requests

URL = "https://official-joke-api.appspot.com/random_joke"


def get_random_joke() -> dict:
    """Fetch a random joke from the Official Joke API.

    Returns:
        dict: The joke data containing 'setup' and 'punchline'.
    """
    try:
        response = requests.get(URL)
        response.raise_for_status()  # Raise an error for HTTP issues

        joke = response.json()

        logger.info("Sucessully fetched joke")
        logger.info(f"Joke type: {joke.get('type')}")
        logger.info(f"{joke.get('setup')} - {joke.get('punchline')}")

        return joke  # Return parsed JSON

    except requests.RequestException as e:
        logger.error(f"Error fetching joke: {e}")
        return {}  # Return an empty dictionary in case of failure


# Example usage
if __name__ == "__main__":
    joke = get_random_joke()
    print(joke)
