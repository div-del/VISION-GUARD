import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from dotenv import load_dotenv
import os

load_dotenv()

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
ALERT_RECEIVER_EMAIL = os.getenv("ALERT_RECEIVER_EMAIL")


def send_alert_email(camera: str, confidence: float, snapshot_path: str, location: str = None):
    """
    Sends an alert email with the snapshot image attached.
    Called automatically when violence is detected.
    """
    try:
        # ── Build email ───────────────────────────────────────
        msg = MIMEMultipart()
        msg["Subject"] = f"🚨 VIOLENCE DETECTED — {camera}"
        msg["From"] = MAIL_FROM
        msg["To"] = ALERT_RECEIVER_EMAIL

        # ── Email body ────────────────────────────────────────
        location_text = location if location else "Unknown"
        body = f"""
        <html>
        <body>
            <h2 style="color:red;">⚠️ Violence Alert Triggered!</h2>
            <table>
                <tr><td><b>Camera</b></td><td>{camera}</td></tr>
                <tr><td><b>Location</b></td><td>{location_text}</td></tr>
                <tr><td><b>Confidence</b></td><td>{confidence * 100:.1f}%</td></tr>
            </table>
            <p>Please check the attached snapshot and take immediate action.</p>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, "html"))

        # ── Attach snapshot image ─────────────────────────────
        if snapshot_path and os.path.exists(snapshot_path):
            with open(snapshot_path, "rb") as f:
                img = MIMEImage(f.read())
                img.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=os.path.basename(snapshot_path)
                )
                msg.attach(img)

        # ── Send via SMTP ─────────────────────────────────────
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.sendmail(MAIL_FROM, ALERT_RECEIVER_EMAIL, msg.as_string())

        print(f"✅ Alert email sent to {ALERT_RECEIVER_EMAIL}")

    except Exception as e:
        print(f"❌ Failed to send email: {e}")
