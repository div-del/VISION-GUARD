import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
ALERT_RECEIVER_EMAIL = os.getenv("ALERT_RECEIVER_EMAIL")


def send_alert_email(camera, confidence, snapshot_path=None, location=None):
    try:
        msg = MIMEMultipart()
        msg["Subject"] = f"VIOLENCE DETECTED — {camera}"
        msg["From"] = MAIL_FROM
        msg["To"] = ALERT_RECEIVER_EMAIL

        location_text = location if location else "Unknown"
        body = f"""
        <html><body>
        <h2 style="color:red;">Violence Alert!</h2>
        <p>Camera: {camera}</p>
        <p>Location: {location_text}</p>
        <p>Confidence: {confidence * 100:.1f}%</p>
        </body></html>
        """
        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.sendmail(MAIL_FROM, ALERT_RECEIVER_EMAIL, msg.as_string())

        print(f"Email sent!")

    except Exception as e:
        print(f"Email failed: {e}")
