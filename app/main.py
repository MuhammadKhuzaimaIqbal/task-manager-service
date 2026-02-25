from fastapi import FastAPI
from app.routers import task_router

# 1. Initialize the FastAPI app with metadata for the Swagger UI
app = FastAPI(
    title="Task Manager API",
    description="A robust REST API for managing tasks with advanced filtering, sorting, and pagination.",
    version="1.0.0",
)

# 2. Include our task router
app.include_router(task_router)

# 3. Add a simple root endpoint (Health check)
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to the Task Manager API!",
        "docs_url": "/docs",
        "status": "Running smoothly "
    }