from uuid import uuid4
import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app import logger
from app.apis.models import TextRequest, StoryResponse
from app.workers.celery_worker import generate_story, generate_video

# from app.core.llm import generate_story_from_moral
# from app.core.generator import generate_video_from_moral


router = APIRouter()


@router.post("/gen_story")
async def gen_story(moral_request: TextRequest):
    moral = moral_request.text.strip()

    if not moral:
        logger.error("Cannot generate story from empty moral.")
        raise HTTPException(status_code=400, detail="Moral cannot be empty")

    # story = generate_story_from_moral(moral)
    task_id = str(uuid4())
    generate_story.apply_async(args=(moral,), task_id=task_id, serializer="json")

    return True


# @router.post("/gen_video")
# async def gen_video(moral_request: TextRequest):
#     moral = moral_request.text.strip()

#     video_path = generate_video_from_moral(moral)

#     if video_path:
#         return FileResponse(video_path, media_type="video/mp4", filename=os.path.basename(video_path))
#     else:
#         raise HTTPException(status_code=404, detail="Video file not found")
