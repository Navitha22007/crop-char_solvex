import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def send_alert(field_id: str, acq_date: str) -> dict:
    """
    Sends an automated email notification regarding an unauthorized crop burn detection.
    Credentials are retrieved safely from environment variables (.env).
    """
    sender_email = os.getenv("EMAIL_ADDRESS", "").strip()
    app_password = os.getenv("EMAIL_APP_PASSWORD", "").strip()
    recipient_email = os.getenv("ALERT_RECIPIENT", "").strip()

    # If recipient is not specified, default to sender
    if not recipient_email and sender_email:
        recipient_email = sender_email

    # Check if credentials are properly configured
    if not sender_email or not app_password or sender_email == "YOUR_DEMO_EMAIL":
        print(f"[ALERT NOTIFIER] Email credentials unconfigured. Alert simulated for field {field_id}.")
        return {
            "status": "simulated",
            "field_id": field_id,
            "message": "Email credentials not set in .env. Alert simulated successfully."
        }

    try:
        subject = "CropChar Alert: Unauthorized Field Burn"
        body = f"""CropChar Automated Alert Notification

Unauthorized burn detected.
Field: {field_id}
Date: {acq_date}

Please inspect the field boundary and take appropriate regulatory or environmental action.
--
CropChar Monitoring System
"""

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Connect to standard Gmail / SMTP server
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", 587))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())

        print(f"[ALERT NOTIFIER] Email alert sent successfully for field {field_id} to {recipient_email}")
        return {
            "status": "sent",
            "field_id": field_id,
            "recipient": recipient_email
        }

    except Exception as e:
        print(f"[ALERT NOTIFIER ERROR] Failed to send email alert: {e}")
        return {
            "status": "error",
            "field_id": field_id,
            "message": f"SMTP dispatch error: {str(e)}"
        }
