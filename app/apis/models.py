from pydantic import BaseModel, Field


class TextRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=250, title="Moral", description="The moral of the story")


class StoryResponse(BaseModel):
    moral: str
    story: str


class TaskResponse(BaseModel):
    task_id: str
    message: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: str | None


class AllTasksResponse(BaseModel):
    tasks: list[TaskStatusResponse]
