import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.api.core.config import get_settings


def send_email(
    to: str,
    subject: str,
    html: str,
):
    settings = get_settings()
    msg = MIMEMultipart()

    msg["From"] = settings.SMTP_FROM
    msg["To"] = to
    msg["Subject"] = subject

    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT,
        ) as server:

            server.starttls()

            server.login(
                settings.SMTP_USERNAME,
                settings.SMTP_PASSWORD,
            )

            server.send_message(msg)

    except Exception as e:
        raise RuntimeError(
            f"Failed to send email: {str(e)}"
        )