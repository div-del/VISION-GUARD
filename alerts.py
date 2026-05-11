from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Alert
from app.schemas import AlertIncoming, AlertResponse, AlertStatusUpdate
from app.utils.email_utils import send_alert_email
import base64
import os
import uuid
from datetime import datetime

router = APIRouter(prefix="/alerts", tags=["Alerts"])

SNAPSHOT_DIR = "snapshots"
os.makedirs(SNAPSHOT_DIR, exist_ok=True)


# ── POST /alerts/ ─────────────────────────────────────────────
# Teammate A calls this when violence is detected
@router.post("/", response_model=AlertResponse)
def receive_alert(alert: AlertIncoming, db: Session = Depends(get_db)):
    """
    Receives alert from Teammate A's ML model.
    Saves snapshot, stores in DB, sends email.
    """

    # Step 1 — Decode and save snapshot image
    snapshot_path = None
    if alert.snapshot:
        try:
            image_data = base64.b64decode(alert.snapshot)
            filename = f"{uuid.uuid4().hex}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            snapshot_path = os.path.join(SNAPSHOT_DIR, filename)
            with open(snapshot_path, "wb") as f:
                f.write(image_data)
            print(f"✅ Snapshot saved: {snapshot_path}")
        except Exception as e:
            print(f"❌ Failed to save snapshot: {e}")

    # Step 2 — Save alert to PostgreSQL
    new_alert = Alert(
        camera=alert.camera,
        confidence=alert.confidence,
        threat_detected=alert.threat_detected,
        snapshot_path=snapshot_path,
        location=alert.location,
        status="unresolved"
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    print(f"✅ Alert saved to DB with ID: {new_alert.id}")

    # Step 3 — Send email notification
    send_alert_email(
        camera=alert.camera,
        confidence=alert.confidence,
        snapshot_path=snapshot_path,
        location=alert.location
    )

    return new_alert


# ── GET /alerts/ ──────────────────────────────────────────────
# Teammate C's dashboard fetches all alerts
@router.get("/", response_model=list[AlertResponse])
def get_all_alerts(db: Session = Depends(get_db)):
    """
    Returns all alerts — used by frontend dashboard.
    """
    alerts = db.query(Alert).order_by(Alert.timestamp.desc()).all()
    return alerts


# ── GET /alerts/{id} ──────────────────────────────────────────
# Get a single alert by ID
@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """
    Returns a single alert by ID.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


# ── PATCH /alerts/{id}/status ─────────────────────────────────
# Teammate C marks alert as resolved
@router.patch("/{alert_id}/status", response_model=AlertResponse)
def update_alert_status(
    alert_id: int,
    update: AlertStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    Update alert status to resolved/unresolved.
    Used by frontend dashboard.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    if update.status not in ["resolved", "unresolved"]:
        raise HTTPException(status_code=400, detail="Status must be 'resolved' or 'unresolved'")

    alert.status = update.status
    db.commit()
    db.refresh(alert)
    print(f"✅ Alert {alert_id} marked as {update.status}")
    return alert


# ── DELETE /alerts/{id} ───────────────────────────────────────
# Delete an alert
@router.delete("/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    """
    Delete an alert by ID.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    db.delete(alert)
    db.commit()
    return {"message": f"Alert {alert_id} deleted successfully"}
