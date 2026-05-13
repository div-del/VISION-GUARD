from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AlertIncoming(BaseModel):
    threat_detected: bool
    confidence: float
    snapshot: str
    camera: str
    time: str
    location: Optional[str] = None

class AlertResponse(BaseModel):
    id: int
    camera: str
    confidence: float
    threat_detected: bool
    snapshot_path: Optional[str]
    timestamp: datetime
    location: Optional[str]
    status: str

    class Config:
        from_attributes = True

class AlertStatusUpdate(BaseModel):
    status: str
