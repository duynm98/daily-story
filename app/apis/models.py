from pydantic import BaseModel, Field


class TextRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=250, title="Moral", description="The moral of the story")


class StoryResponse(BaseModel):
    moral: str
    story: str
