from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    camera = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    threat_detected = Column(Boolean, default=True)
    snapshot_path = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    location = Column(String, nullable=True)
    status = Column(String, default="unresolved")