# CCTV Frontend — Teammate C Files

## Files

| File | Purpose |
|------|---------|
| `index.html` | Main live monitoring dashboard |
| `heatmap.html` | Threat heatmap + zone analytics |
| `alerts.html` | Alert feed + incident detail + dispatch |

## How to Run

Just open `index.html` in a browser — no build step needed. All CSS/JS is inline.

Links between pages use relative hrefs, so keep all 3 files in the same folder.

## Backend Integration Points

Replace these simulated values with real API calls:

### 1. Live camera feeds
In `index.html`, the canvas renders simulated video. Replace with:
```js
// Connect to Teammate B's stream endpoint
const video = document.createElement('video');
video.src = 'http://localhost:8000/stream/cam1'; // FastAPI MJPEG stream
```

### 2. Alert feed
Alerts are hardcoded. Replace with:
```js
// Poll or WebSocket from Teammate B
async function fetchAlerts() {
  const res = await fetch('http://localhost:8000/api/alerts');
  const data = await res.json();
  return data.alerts;
}
// Or WebSocket:
const ws = new WebSocket('ws://localhost:8000/ws/alerts');
ws.onmessage = (e) => { const alert = JSON.parse(e.data); addAlert(alert); };
```

### 3. Detection confidence bars
```js
async function fetchDetectionStats() {
  const res = await fetch('http://localhost:8000/api/detection/current');
  return res.json(); // { behaviors: [{ label, confidence }] }
}
```

### 4. Dispatch police
```js
async function dispatchPolice(incidentId, location) {
  await fetch('http://localhost:8000/api/dispatch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ incident_id: incidentId, gps: location })
  });
}
```

### 5. Heatmap data
```js
async function fetchHeatmapData(mode='all', hours=24) {
  const res = await fetch(`http://localhost:8000/api/heatmap?mode=${mode}&hours=${hours}`);
  return res.json(); // { hotspots: [{ x, y, intensity, name, count }] }
}
```

## Expected API response shapes (from Teammate B)

```json
// GET /api/alerts
{
  "alerts": [
    {
      "id": "INC-0047",
      "severity": "critical",
      "type": "Aggressive Behavior",
      "camera_id": "cam2",
      "zone": "Platform A",
      "timestamp": "2026-04-08T19:34:00",
      "confidence": 91,
      "dispatch_status": "dispatched",
      "gps": { "lat": 12.9716, "lon": 77.5946 },
      "description": "..."
    }
  ]
}

// GET /api/detection/current
{
  "behaviors": [
    { "label": "Aggression", "confidence": 87 },
    { "label": "Screaming", "confidence": 72 }
  ]
}

// POST /api/dispatch → 200 OK
```

## Stack
- Pure HTML + CSS + JS (no framework needed for demo)
- Fonts: Syne + Space Mono via Google Fonts
- Canvas API for video simulation + heatmap
- WebSocket-ready architecture
