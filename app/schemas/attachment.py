from pydantic import BaseModel, ConfigDict
from datetime import datetime

class AttachmentResponse(BaseModel):
    id: int
    task_id: int
    filename: str
    original_name: str
    content_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)