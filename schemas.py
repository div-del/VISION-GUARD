from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ── What Teammate A sends to /alert ──────────────────────────
class Alertincoming(BaseModel):
    threat_detected: bool
    confidence: float
    snapshot: str           # base64 encoded image string
    camera: str             # e.g. "Camera 1"
    time: str               # e.g. "Now" or actual timestamp
    location: Optional[str] = None  # optional camera location

# ── What we store and return back ────────────────────────────
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
        from_attributes = True  # allows SQLAlchemy model → Pydantic conversion

# ── For updating alert status ─────────────────────────────────
class AlertStatusUpdate(BaseModel):
    status: str             # "resolved" or "unresolved"
