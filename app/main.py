from fastapi import FastAPI
from app.routers import task_router, auth_router, admin_router
from app.database import engine, Base
from app import models  # VERY IMPORTANT
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title="Task Manager API",
    description="A robust REST API for managing tasks with advanced filtering, sorting, and pagination.",
    version="1.0.0",
)

# Create the directory if it doesn't exist
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# Mount the static files directory
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(task_router)

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to the Task Manager API!",
        "docs_url": "/docs",
        "status": "Running smoothly",
    }