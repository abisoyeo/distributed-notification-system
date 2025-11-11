from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import Optional

class PushMessage(BaseModel):
    request_id: str
    user_id: str
    template_code: str
    variables: dict
    priority: int = 5
    metadata: dict | None = None

class NotificationStatus(str, Enum):
    delivered = 'delivered'
    pending = 'pending'
    failed = 'failed'

class NotificationStatusResponse(BaseModel):
    notification_id: str
    status: NotificationStatus
    timestamp: Optional[datetime]
    error: Optional[str]

