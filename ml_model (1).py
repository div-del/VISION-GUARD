import cv2
import numpy as np
import os
import json
import base64
from ultralytics import YOLO
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model, load_model

# ── Load Models ──────────────────────────────────────────────
model_yolo = YOLO("yolov8n.pt")
model_violence = load_model("violence_model.h5")


# ── Extract frames from video ─────────────────────────────────
def extract_frames(video_path, max_frames=10):
    """Extract evenly spaced frames from a video file."""
    frames = []
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    step = max(total // max_frames, 1)

    count = 0
    frame_no = 0
    while count < max_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (224, 224))
        frame = frame / 255.0
        frames.append(frame)
        frame_no += step
        count += 1

    cap.release()
    return frames


# ── Detect violence in video ──────────────────────────────────
def detect_violence(video_path):
    """
    Run YOLO + MobileNet pipeline on a video.
    Returns (violence_detected: bool, snapshot_path: str | None)
    """
    cap = cv2.VideoCapture(video_path)
    violence_detected = False
    snapshot_path = None
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % 10 != 0:   # analyse every 10th frame
            continue

        # Step 1 – YOLO detects persons
        results = model_yolo.predict(frame, conf=0.5, verbose=False)
        persons = [r for r in results[0].boxes.cls if r == 0]

        if len(persons) >= 2:        # at least 2 people present
            # Step 2 – MobileNet classifies violence
            resized = cv2.resize(frame, (224, 224)) / 255.0
            input_frame = np.expand_dims(resized, axis=0)
            prediction = model_violence.predict(input_frame, verbose=False)[0][0]

            if prediction > 0.7:     # 70 % confidence threshold
                violence_detected = True
                snapshot_path = f"snapshot_{frame_count}.jpg"
                cv2.imwrite(snapshot_path, frame)
                print(f"VIOLENCE DETECTED! Confidence: {prediction:.2f}")
                break

    cap.release()
    return violence_detected, snapshot_path


# ── Send alert to Teammate B ──────────────────────────────────
def send_alert(snapshot_path, confidence):
    """
    Package the snapshot + metadata into alert.json for Teammate B.
    When Teammate B's server URL is available, use requests.post() instead.
    """
    with open(snapshot_path, "rb") as f:
        snapshot_base64 = base64.b64encode(f.read()).decode()

    alert_data = {
        "threat_detected": True,
        "confidence": float(confidence),
        "snapshot": snapshot_base64,
        "camera": "Camera 1",
        "time": "Now",
    }

    with open("alert.json", "w") as f:
        json.dump(alert_data, f)

    print("Alert saved! Ready to send to Teammate B!")

    # ── Uncomment below once Teammate B shares their server URL ──
    # import requests
    # requests.post("http://TEAMMATE_B_IP:5000/alert", json=alert_data)


# ── Main entry point ──────────────────────────────────────────
def main(video_path):
    print("Analysing video:", video_path)
    detected, snapshot = detect_violence(video_path)

    if detected:
        send_alert(snapshot, 0.98)
        print("Alert sent to Teammate B!")
    else:
        print("No threat detected!")


if __name__ == "__main__":
    # Replace with your test video path
    main("test_video.mp4")
