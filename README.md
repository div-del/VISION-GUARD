# VISION-GUARD 🛡️

> AI-powered Smart CCTV system that detects violent and suspicious behavior in real time, triggers automated alerts, and notifies law enforcement instantly.

---

## What It Does

VisionGuard continuously monitors CCTV feeds using a trained deep learning model. When it detects aggression, violence, loitering, or distress signals, it:

- Captures a snapshot of the incident
- Stores the alert with timestamp, camera ID, GPS location, and confidence score
- Sends an automated email notification to security personnel
- Exposes the alert data to a live dashboard for monitoring and dispatch

---

## Repository Structure

This repo has 3 branches — one per component:

| Branch | Owner | Description |
|--------|-------|-------------|
| `ML-Model` | Teammate A | Violence detection model (Keras/TF), inference pipeline |
| `backend` | Teammate B | FastAPI server, PostgreSQL DB, alert engine, email notifications |
| `frontend` | Teammate C | Live dashboard, alert feed, threat heatmap |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| ML Model | Python, TensorFlow/Keras, OpenCV, `violence_model.h5` |
| Backend | FastAPI, SQLAlchemy, PostgreSQL, FastAPI-Mail, Uvicorn |
| Frontend | HTML, CSS, Vanilla JS, Canvas API |
| Deployment | Render (backend), static hosting (frontend) |

---

## Branch: ML-Model

Trains and runs the violence detection model on live video frames.

**Files:**
- `violence_model.h5` — trained Keras model
- `ml_model.py` — loads model, runs inference on frames, POSTs alerts to backend
- `Smart_cctv.ipynb` — training notebook

**How it works:**
1. Captures frames from CCTV feed via OpenCV
2. Runs frame through `violence_model.h5`
3. If confidence > threshold → POSTs to `POST /alerts/` with camera ID, confidence, base64 snapshot, and location

---

## Branch: backend

FastAPI server that receives alerts, stores them, and notifies security.

**Files:**
- `main.py` — app entry point, CORS, route registration
- `alerts.py` → `app/routes/alerts.py` — all alert endpoints
- `models.py` — SQLAlchemy `Alert` table definition
- `database.py` — DB engine and session
- `schemas.py` — Pydantic request/response models
- `email_utils.py` — sends email on new alert
- `render.yaml` — Render deployment config

**API Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/alerts/` | Receive alert from ML model |
| `GET` | `/alerts/` | Fetch all alerts (used by dashboard) |
| `GET` | `/alerts/{id}` | Get single alert |
| `PATCH` | `/alerts/{id}/status` | Mark resolved/unresolved |
| `DELETE` | `/alerts/{id}` | Delete alert |
| `GET` | `/snapshots/{filename}` | Serve incident snapshot image |

**Run locally:**
```bash
# Create app/ structure (see backend README for details)
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# API docs at: http://localhost:8000/docs
```

---

## Branch: frontend

Live monitoring dashboard — no framework, pure HTML/CSS/JS.

**Files:**
- `index.html` — main live CCTV dashboard with 4-camera grid, alert feed, detection confidence bars
- `alerts.html` — full incident log with search, filters, detail panel, dispatch button
- `heatmap.html` — threat heatmap with zone intensity, hotspot rankings, hourly volume chart

**Features:**
- Polls `GET /alerts/` every 10 seconds for live updates
- Dispatch button POSTs incident payload (GPS, camera, confidence, timestamp) to police webhook
- Mark Resolved calls `PATCH /alerts/{id}/status`
- Falls back to demo data if backend is unreachable

**Run locally:**
```bash
python -m http.server 5500
# Open: http://localhost:5500
```

---

## Running the Full System Locally

**Terminal 1 — Backend:**
```bash
git checkout backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
git checkout frontend
python -m http.server 5500
```

**Terminal 3 — ML Model (optional for demo):**
```bash
git checkout ML-Model
python ml_model.py
```

Open `http://localhost:5500` — dashboard fetches live alerts from backend.

---

## Environment Variables (backend `.env`)

```env
DATABASE_URL=postgresql://user:password@host:5432/smart_cctv
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_FROM=your@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
ALERT_RECEIVER_EMAIL=security@example.com
```

For local testing without PostgreSQL, use:
```env
DATABASE_URL=sqlite:///./smart_cctv.db
```

---

## Team

| Role | Branch | Responsibilities |
|------|--------|-----------------|
| ML & AI Core | `ML-Model` | Model training, CV pipeline, inference, audio detection- Poorvika |
| Backend & System | `backend` | FastAPI server, DB, alert engine, email, deployment- Pranatha |
| Frontend & Dashboard | `frontend` | Dashboard UI, alert feed, heatmap, demo- Nameeta |

---

## Demo

- **Live Dashboard:** real-time camera feeds with bounding box overlays, behavior detection confidence scores
- **Alert Feed:** incident log with severity filtering, GPS coordinates, event timeline
- **Dispatch:** clicking Dispatch sends full incident payload to a live webhook endpoint — demonstrating real-time police notification
- **Heatmap:** shows threat hotspots across camera zones over the last 24 hours
