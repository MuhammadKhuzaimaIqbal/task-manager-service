import os
import asyncio
import uuid
from fastapi import UploadFile, File
import shutil
from pathlib import Path
from fastapi import WebSocket, WebSocketDisconnect # Add these imports

from app.models.attachment import Attachment
from app.routers.auth import CurrentUser
from app.schemas.attachment import AttachmentResponse

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc, delete
from typing import List, Optional,Annotated

from app.database import get_db
from app.models.task import Task, TaskStatus, TaskPriority
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.routers.auth import get_current_user # Import the function, not just the alias
from app.models.user import User  # Add this 
from fastapi import BackgroundTasks # Add this import

router = APIRouter(prefix="/tasks", tags=["Tasks"])

class ConnectionManager:
    def __init__(self):
        # List to store active websocket connections
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        # Send message to all connected clients
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@router.websocket("/ws/tasks")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We keep the connection open. 
            # Usually, we just wait for data or a heartbeat.
            await websocket.receive_text() 
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# This is our simulated "worker" function
async def send_task_notification(email: str, task_title: str):
    # Simulate a delay (e.g., connecting to an email server)
    await asyncio.sleep(2) 
    print(f"--- SIMULATED EMAIL SENT ---")
    print(f"To: {email}")
    print(f"Subject: New Task Assigned")
    print(f"Body: Hello! You have been assigned a new task: '{task_title}'")
    print(f"----------------------------")

@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    task_in: TaskCreate,
    current_user: CurrentUser,
    background_tasks: BackgroundTasks, # Add this parameter
    db: AsyncSession = Depends(get_db)
):
    new_task = Task(
        **task_in.model_dump(),
        user_id=current_user.id
    )

    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    # Trigger the background task
    # It will run AFTER the response is sent to the user
    background_tasks.add_task(
        send_task_notification, 
        current_user.email, 
        new_task.title
    )

    return new_task

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    sort_by: str = Query("created_at", description="Field to sort by (e.g., created_at, due_date, title)"),
    order: str = Query("desc", description="Sort order: 'asc' or 'desc'"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Task)
    
    if status:
        stmt = stmt.where(Task.status == status)
    if priority:
        stmt = stmt.where(Task.priority == priority)
        
    sort_column = getattr(Task, sort_by, Task.created_at) 
    if order.lower() == "desc":
        stmt = stmt.order_by(desc(sort_column))
    else:
        stmt = stmt.order_by(asc(sort_column))
        
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)
    
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task

@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        
    update_data = task_update.model_dump(exclude_unset=True)
    
    # Check if status is being changed
    old_status = task.status

    for key, value in update_data.items():
        setattr(task, key, value)
        
    await db.commit()
    await db.refresh(task)

    # If the status changed, broadcast the update!
    if "status" in update_data and old_status != task.status:
        await manager.broadcast({
            "event": "TASK_STATUS_UPDATED",
            "task_id": task.id,
            "new_status": task.status,
            "title": task.title
        })

    return task

@router.put("/{task_id}", response_model=TaskResponse)
async def replace_task(task_id: int, task_in: TaskCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        
    update_data = task_in.model_dump()
    
    for key, value in update_data.items():
        setattr(task, key, value)
        
    await db.commit()
    await db.refresh(task)
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        
    await db.delete(task)
    await db.commit()


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_tasks(db: AsyncSession = Depends(get_db)):
    await db.execute(delete(Task))
    await db.commit()

# Define the upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Allowed constraints
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
ALLOWED_CONTENT_TYPES = {"application/pdf", "image/png", "image/jpeg"}

@router.post("/test-single-upload")
async def test_upload(file: UploadFile = File(...)):
    return {"filename": file.filename}

@router.post("/{task_id}/attachments", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
async def upload_task_attachment(
    task_id: int,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # 1. Check if the task exists and belongs to the user (or admin)
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Optional: Security check to ensure user owns the task
    if task.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to attach files to this task")

    # 2. Validate File Extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid file type. Only PDF, PNG, and JPG are allowed."
        )

    # 3. Validate Content Type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Invalid MIME type")

    # 4. Validate File Size
    # We read the size from the file descriptor
    file.file.seek(0, 2)  # Move to end of file
    file_size = file.file.tell()  # Get position (size)
    file.file.seek(0)  # Reset to beginning for saving
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max size is 5MB")

    # 5. Generate UUID filename and Save to Disk
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")

    # 6. Store Metadata in DB
    new_attachment = Attachment(
        task_id=task_id,
        filename=unique_filename,
        original_name=file.filename,
        content_type=file.content_type
    )

    db.add(new_attachment)
    await db.commit()
    await db.refresh(new_attachment)

    return new_attachment

# app/routers/task.py

@router.get("/{task_id}/attachments", response_model=List[AttachmentResponse])
async def list_task_attachments(
    task_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    # 1. Check if task exists
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 2. Fetch attachments
    result = await db.execute(
        select(Attachment).where(Attachment.task_id == task_id)
    )
    attachments = result.scalars().all()

    # 3. Add download URLs (We'll update the Schema next to support this)
    return attachments


