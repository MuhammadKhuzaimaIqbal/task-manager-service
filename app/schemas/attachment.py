from pydantic import BaseModel, ConfigDict, computed_field
from datetime import datetime
class AttachmentResponse(BaseModel):
    id: int
    task_id: int
    filename: str
    original_name: str
    content_type: str
    created_at: datetime

    @computed_field
    @property
    def download_url(self) -> str:
        return f"/uploads/{self.filename}"

    model_config = ConfigDict(from_attributes=True)