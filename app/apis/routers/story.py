from uuid import uuid4
import os
from datetime import datetime

from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app import logger
from app.apis.models import TextRequest, StoryResponse, TaskResponse, TaskStatusResponse, AllTasksResponse
from app.db.redis_db import database
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

    # Store task_id in Redis set
    database.sadd("celery_task_ids", task_id)

    generate_story.apply_async(args=(moral,), task_id=task_id, serializer="json")

    return TaskResponse(task_id=task_id, message="Task in progress")


@router.post("/gen_video")
async def gen_video(moral_request: TextRequest):
    moral = moral_request.text.strip()

    if not moral:
        logger.error("Cannot generate story from empty moral.")
        raise HTTPException(status_code=400, detail="Moral cannot be empty")

    task_id = datetime.now().strftime("%Y_%m_%d_%H_%M")
    
    database.sadd("celery_task_ids", task_id)

    generate_video.apply_async(args=(moral, task_id), task_id=task_id, serializer="json")

    return TaskResponse(task_id=task_id, message="Task in progress")


@router.get("/task_status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Fetch the status of a Celery task using its task_id.

    Args:
        task_id (str): The unique identifier of the task.

    Returns:
        TaskStatusResponse: The task status and result (if completed).
    """
    task_result = AsyncResult(task_id)

    if task_result is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskStatusResponse(task_id=task_id, status=task_result.status, result=task_result.result if task_result.successful() else None)


@router.get("/all_tasks", response_model=AllTasksResponse)
async def get_all_tasks():
    """
    Fetch all stored Celery tasks and their statuses.
    """
    if database is None:
        raise HTTPException(status_code=500, detail="Redis database is not initialized")

    task_ids = database.smembers("celery_task_ids")  # Retrieve all stored task IDs

    if not task_ids:
        return {"tasks": []}  # Return empty list if no tasks exist

    all_tasks = []
    for task_id in task_ids:
        task_result = AsyncResult(task_id)
        all_tasks.append(
            TaskStatusResponse(task_id=task_id, status=task_result.status, result=task_result.result if task_result.successful() else None)
        )

    return {"tasks": all_tasks}
