from fastapi import FastAPI
from app.routers import task_router, auth_router, admin_router

app = FastAPI(
    title="Task Manager API",
    description="A robust REST API for managing tasks with advanced filtering, sorting, and pagination.",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(task_router)


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to the Task Manager API!",
        "docs_url": "/docs",
        "status": "Running smoothly ",
    }