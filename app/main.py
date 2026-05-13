from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.routes import alerts
import os

# ── Create all DB tables on startup ──────────────────────────
Base.metadata.create_all(bind=engine)

# ── Init FastAPI app ──────────────────────────────────────────
app = FastAPI(
    title="Smart CCTV Backend API",
    description="Backend for AI Smart CCTV Violence Detection System",
    version="1.0.0"
)

# ── CORS — allows Teammate C's frontend to call this API ──────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Serve snapshots as static files ──────────────────────────
# Teammate C can display images via: http://localhost:8000/snapshots/filename.jpg
os.makedirs("snapshots", exist_ok=True)
app.mount("/snapshots", StaticFiles(directory="snapshots"), name="snapshots")

# ── Register routes ───────────────────────────────────────────
app.include_router(alerts.router)


# ── Root health check ─────────────────────────────────────────
@app.get("/")
def root():
    return {
        "status": "✅ Smart CCTV Backend is running",
        "docs": "/docs",
        "endpoints": {
            "receive_alert": "POST /alerts/",
            "get_all_alerts": "GET /alerts/",
            "get_alert": "GET /alerts/{id}",
            "update_status": "PATCH /alerts/{id}/status",
            "delete_alert": "DELETE /alerts/{id}",
        }
    }
