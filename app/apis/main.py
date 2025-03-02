from fastapi import FastAPI

from app.apis.routers import tasks

app = FastAPI()

app.include_router(tasks.router)

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to the Short Video Generator API. Go to /docs for more detail"}
