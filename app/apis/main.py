from fastapi import FastAPI

from app.apis.routers import story

app = FastAPI()

app.include_router(story.router)

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to the Short Video Generator API. Go to /docs for more detail"}
