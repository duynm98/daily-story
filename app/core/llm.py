import json
import re
from typing import List

import g4f
from loguru import logger

from app import config

_max_retries = 3

_temperature = config["llm"].get("temperature", 1.0)
_max_story_words = config["story"].get("max_words", 200)
_language = config["video"].get("language", "English")


def _generate_response(prompt: str) -> str:
    i = 0

    while i < _max_retries:
        try:
            content = ""
            logger.info(f"Using g4f as llm provider")
            logger.info("=" * 100)
            logger.info("prompt: " + prompt)

            content = g4f.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=_temperature,
            )

            logger.success(f"Successfully generate response from llm")
            return content.replace("\n", ". ")
        except Exception as e:
            logger.error(f"Cannot generate response: {e}")
            i += 1
            logger.info(f"Retrying attemp #{i + 1}")

    return ""


def generate_script(video_subject: str, language: str = "", paragraph_number: int = 1) -> str:
    prompt = f"""
# Role: Video Script Generator

## Goals:
Generate a script to provide more informations that supports the subject of the video.

## Constrains:
1. the script is to be returned as a string with the specified number of paragraphs.
2. do not under any circumstance reference this prompt in your response.
3. get straight to the point, don't start with unnecessary things like, "welcome to this video".
4. you must not include any type of markdown or formatting in the script, never use a title.
5. only return the raw content of the script.
6. do not include "voiceover", "narrator" or similar indicators of what should be spoken at the beginning of each paragraph or line.
7. you must not mention the prompt, or anything about the script itself. also, never talk about the amount of paragraphs or lines. just write the script.
8. respond in the same language as the video subject.
9. the script must consist 80-100 words
10. the scipt must start with "Did you know: {video_subject}"

# Initialization:
- video subject: {video_subject}
- number of paragraphs: {paragraph_number}
""".strip()
    if language:
        prompt += f"\n- language: {language}"

    final_script = ""
    logger.info(f"subject: {video_subject}")

    def format_response(response):
        # Clean the script
        # Remove asterisks, hashes
        response = response.replace("*", "")
        response = response.replace("#", "")

        # Remove markdown syntax
        response = re.sub(r"\[.*\]", "", response)
        response = re.sub(r"\(.*\)", "", response)

        # Split the script into paragraphs
        paragraphs = response.split("\n\n")

        # Select the specified number of paragraphs
        # selected_paragraphs = paragraphs[:paragraph_number]

        # Join the selected paragraphs into a single string
        return "\n\n".join(paragraphs)

    for i in range(_max_retries):
        try:
            response = _generate_response(prompt=prompt)
            if response:
                final_script = format_response(response)
            else:
                logger.error("gpt returned an empty response")

            # g4f may return an error message
            if final_script and "当日额度已消耗完" in final_script:
                raise ValueError(final_script)

            if final_script:
                break
        except Exception as e:
            logger.error(f"failed to generate script: {e}")

        if i < _max_retries:
            logger.warning(f"failed to generate video script, trying again... {i + 1}")
    if "Error: " in final_script:
        logger.error(f"failed to generate video script: {final_script}")
    else:
        logger.success(f"completed: \n{final_script}")
    return final_script.strip()


def generate_terms(content: str, amount: int = 3) -> List[str]:
    prompt = f"""
# Role: Video Search Terms Generator

## Goals:
Generate {amount} search terms for searching images to tell the provided story.

## Constrains:
1. Return search terms as a JSON array of strings.
2. The first term must be the story's main character. Each additional term (1-3 words) must include the main character, other characters, or the scene.
3. Only return the JSON array—nothing else, not the script.
4. Search terms must closely relate to the story's characters or scene.
5. Use English search terms only.
6. Each term must be a concrete noun and must not be names of characters.

## Output Example:
["search term 1", "search term 2", "search term 3"]

## The story:
{content}

Please note that you must use English for generating video search terms; Chinese is not accepted.
""".strip()

    # logger.info(f"subject: {video_subject}")

    search_terms = []
    response = ""
    for i in range(_max_retries):
        try:
            response = _generate_response(prompt)
            if "Error: " in response:
                logger.error(f"failed to generate video script: {response}")
                return []
            search_terms = json.loads(response)
            if not isinstance(search_terms, list) or not all(isinstance(term, str) for term in search_terms):
                logger.error("response is not a list of strings.")
                continue

        except Exception as e:
            logger.warning(f"failed to generate video terms: {str(e)}")
            if response:
                match = re.search(r"\[.*]", response)
                if match:
                    try:
                        search_terms = json.loads(match.group())
                    except Exception as e:
                        logger.warning(f"failed to generate video terms: {str(e)}")
                        pass

        if search_terms and len(search_terms) > 0:
            break
        if i < _max_retries:
            logger.warning(f"failed to generate video terms, trying again... {i + 1}")

    logger.success(f"completed: \n{search_terms}")
    return search_terms


def generate_story_from_moral(moral: str, example: str = "") -> str:
    prompt = f"""
# Role: Short Story Generator

## Goal:
Generate a short story that show the provided moral.

## Constrains:
1. the story is to be returned as a plain text.
2. the story must have unexpected plots
3. do not under any circumstance reference this prompt in your response.
4. get straight to the point, don't start with unnecessary things like, "here is a story...".
5. you must not include any type of markdown or formatting in the story, never use a title.
6. only return the raw content of the story.
7. do not include "voiceover", "narrator" or similar indicators of what should be spoken at the beginning of each paragraph or line.
8. you must not mention the prompt, or anything about the script itself. also, never talk about the amount of paragraphs or lines. just write the story.
9. respond must in {_language}.
10. the story must consist at most {_max_story_words} words

## Moral:
{moral}
"""

    if example:
        prompt += f"\n## Output Example:\n{example}"

    def format_response(response):
        # Clean the script
        # Remove asterisks, hashes
        response = response.replace("*", "")
        response = response.replace("#", "")

        # Remove markdown syntax
        response = re.sub(r"\[.*\]", "", response)
        response = re.sub(r"\(.*\)", "", response)

        # Split the script into paragraphs
        paragraphs = response.split("\n\n")

        # Select the specified number of paragraphs
        # selected_paragraphs = paragraphs[:paragraph_number]

        # Join the selected paragraphs into a single string
        return "\n\n".join(paragraphs)

    for i in range(_max_retries):
        try:
            response = _generate_response(prompt=prompt)
            if response:
                final_story = format_response(response)
            else:
                logger.error("gpt returned an empty response")

            # g4f may return an error message
            if final_story and "error:" in final_story.lower().strip():
                raise ValueError(final_story)

            if final_story:
                break

        except Exception as e:
            logger.error(f"failed to generate story: {e}")

        if i < _max_retries:
            logger.warning(f"failed to generate story, trying again... {i + 1}")

    if "error: " in final_story:
        logger.error(f"failed to generate story for moral: {moral}")
    else:
        logger.success(f"A story for moral '{moral}' has been generated:")

    return final_story.strip()


def translate_to_vietnamese(content: str) -> str:
    prompt = f"""
# Role: Translator

## Goals:
Translate the provided paragraph to Vietnamese.

## Constrains:
1. the translation is always returned as a plain text.
2. you must only return the translation. you must not return anything else.
3. the translation must contain only vietnamese words.

## Paragraph:
{content}

""".strip()

    # logger.info(f"subject: {video_subject}")

    response = ""
    for i in range(_max_retries):
        try:
            response = _generate_response(prompt)
            if "Error: " in response:
                logger.error(f"failed to translate: {response}")
                return ""

            if not isinstance(response, str):
                logger.error("response is not a string.")
                continue

        except Exception as e:
            logger.warning(f"failed to translate: {str(e)}")

        if response:
            break

        if i < _max_retries:
            logger.warning(f"failed to generate video terms, trying again... {i + 1}")

    logger.success(f"Vietnamese translation: \n{response}")
    return response


if __name__ == "__main__":
    joke = _generate_response(
        """
Generate a random dad joke. Explain why the joke is funny. Avoid the following jokes:
- Why did the scarecrow win an award?
"""
    )
    print(joke)
