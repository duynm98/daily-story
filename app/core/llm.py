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
2. The first term must be the story's main character. Each additional term (1-3 words) must include other characters or the place where the story happens.
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
2. the story must have unexpected plots. The characters have to be animals.
3. do not under any circumstance reference this prompt in your response.
4. get straight to the point, don't start with unnecessary things like, "here is a story...".
5. you must not include any type of markdown or formatting in the story, never use a title.
6. only return the raw content of the story.
7. you must not mention the prompt
8. respond must in {_language}.
9. the story must consist at most {_max_story_words} words

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
    response = _generate_response(
        """
I need pictures for my bedtime story. Give me a list of prompt to generate such images for my story. The story:
```
### **The Brave Little Monkey and the Hidden Treasure**  

**[Opening Scene: Jungle at Sunset]**  
The sun was setting over the vast jungle, painting the sky in shades of orange and pink. Deep in the heart of the jungle lived a small but courageous monkey named Milo. Unlike the other monkeys who spent their days swinging from tree to tree, Milo dreamed of adventure.  

One evening, as he sat by the river, an old tortoise named Taro approached him.  
*"Milo,"* Taro said in a hushed voice, *"have you ever heard of the Hidden Treasure of the Golden Banana?"*  

Milo’s eyes widened. *"Golden Banana? What’s that?"*  

Taro smiled. *"Long ago, a legendary golden banana was hidden deep inside the Dark Cavern. But it is guarded by the Shadow Panther, and no one has ever been brave enough to retrieve it."*  

Milo's heart pounded with excitement. This was the adventure he had been waiting for!  

---  

### **The Journey Begins**  

Early the next morning, Milo packed a small bag of bananas, took a deep breath, and set off toward the Dark Cavern. As he traveled through the dense jungle, he faced many obstacles.  

First, he had to cross the **Whispering River**, where sneaky crocodiles lurked beneath the water. Carefully, he used hanging vines to swing across, just barely escaping a snapping jaw!  

Then, he entered the **Twisting Trees**, a maze-like forest filled with moving branches. Thinking fast, he followed the path of fireflies, who lit the way through the darkness.  

Finally, he reached the **Dark Cavern**, an enormous cave with eerie glowing eyes staring from the shadows.  

---  

### **Facing the Shadow Panther**  

Milo stepped inside cautiously. Suddenly, a deep growl echoed through the cavern. The **Shadow Panther** emerged, its glowing yellow eyes locked onto Milo.  

*"Who dares enter my cave?"* the Panther snarled.  

Milo gulped but stood his ground. *"I am Milo, and I have come to find the Golden Banana!"*  

The Panther chuckled. *"To claim the treasure, you must pass the **Test of Courage**. If you fail, you must leave forever."*  

Milo nodded bravely. *"I accept the challenge!"*  

---  

### **The Test of Courage**  

The cave suddenly filled with **darkness**. Milo couldn't see a thing. A voice whispered, *"Find the treasure, but do not be afraid."*  

Milo took a deep breath. Instead of panicking, he focused on his other senses—his **ears** picked up the sound of the wind, and his **hands** felt along the cave walls. He walked slowly until he felt something **smooth and round**.  

Light filled the cavern as Milo lifted the **Golden Banana** into the air! The Shadow Panther grinned.  

*"You have proven your bravery, little monkey. The treasure is yours."*  

---  

### **The Hero Returns**  

Milo raced back to the jungle, where the animals gathered to cheer for him. Taro the Tortoise smiled proudly. *"You did it, Milo! You showed us all that true bravery comes from within."*  

From that day on, Milo was no longer just a small monkey—he was **Milo the Brave**, the hero of the jungle!  

**THE END.**  

---
### **Goodnight, Little Adventurer!**  
Now close your eyes and dream of your own adventure. Who knows? Maybe one day, you'll find your own Golden Banana! 🌙✨
```
"""
    )
    print(response)
