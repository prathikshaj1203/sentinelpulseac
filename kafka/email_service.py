import smtplib

from email.mime.text import MIMEText

from email.mime.multipart import MIMEMultipart

import os

from dotenv import load_dotenv

load_dotenv()

# =========================================
# SEND ALERT EMAIL
# =========================================

def send_alert_email(

    machine_id,

    risk_level,

    failure_probability,

    temperature,

    vibration

):

    sender_email = os.getenv(

        "EMAIL_USER"

    )

    sender_password = os.getenv(

        "EMAIL_PASSWORD"

    )

    receiver_email = os.getenv(

        "ALERT_RECEIVER"

    )

    subject = f"""

CRITICAL HVAC ALERT:
{machine_id}

"""

    body = f"""

Critical machine anomaly detected.

Machine ID:
{machine_id}

Risk Level:
{risk_level}

Failure Probability:
{failure_probability:.2f}%

Temperature:
{temperature:.2f}°C

Vibration:
{vibration:.2f}

Immediate inspection recommended.

SentinelPulse AI Monitoring System
"""

    msg = MIMEMultipart()

    msg["From"] = sender_email

    msg["To"] = receiver_email

    msg["Subject"] = subject

    msg.attach(

        MIMEText(

            body,

            "plain"

        )

    )

    try:

        server = smtplib.SMTP(

            "smtp.gmail.com",

            587

        )

        server.starttls()

        server.login(

            sender_email,

            sender_password

        )

        server.send_message(msg)

        server.quit()

        print(

            f"📧 Email alert sent for {machine_id}"

        )

    except Exception as smtp_err:

        print(

            f"⚠️ Could not send email alert for {machine_id}: {smtp_err}"

        )