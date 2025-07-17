from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NotificationCreate(BaseModel):
    text: str
    status: Optional[str] = None
    error: Optional[str] = None
    sent_at: Optional[datetime] = None
    comment: Optional[str] = None


class NotificationUpdate(BaseModel):
    text: Optional[str] = None
    status: Optional[str] = None
    error: Optional[str] = None
    sent_at: Optional[datetime] = None
    comment: Optional[str] = None


class NotificationDTO(NotificationCreate):
    id: int

    model_config = {"from_attributes": True}
