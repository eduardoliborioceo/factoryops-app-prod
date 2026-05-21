from flask import current_app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email
import smtplib
from email.message import EmailMessage


def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Estratégia de providers (em ordem de prioridade):
    1) Resend API  — usa HTTPS, funciona no Railway
    2) SendGrid    — usa HTTPS, funciona no Railway
    3) SMTP        — bloqueado pelo Railway (Network unreachable)
    """

    config = current_app.config
    to_email = (to_email or "").strip()
    subject = (subject or "").strip()

    if not to_email or not subject:
        current_app.logger.warning("Email not sent: missing recipient or subject.")
        return False

    # -----------------------
    # Resend (recomendado)
    # -----------------------
    if config.get("RESEND_API_KEY") and config.get("RESEND_FROM"):
        try:
            import requests as http_client
            payload = {
                "from": config["RESEND_FROM"],
                "to": [to_email],
                "subject": subject,
                "text": body or "",
            }
            reply_to = config.get("RESEND_REPLY_TO")
            if reply_to:
                payload["reply_to"] = reply_to

            response = http_client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {config['RESEND_API_KEY']}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=15,
            )
            if response.status_code in (200, 201):
                return True
            current_app.logger.error(f"Resend error: {response.status_code} {response.text}")
            return False
        except Exception as e:
            current_app.logger.error(f"Resend error: {e}")
            return False

    # -----------------------
    # SendGrid
    # -----------------------
    if config.get("SENDGRID_API_KEY") and config.get("SENDGRID_FROM"):
        try:
            message = Mail(
                from_email=Email(config["SENDGRID_FROM"]),
                to_emails=to_email,
                subject=subject,
                plain_text_content=body or "",
            )

            reply_to = config.get("SENDGRID_REPLY_TO")
            if reply_to:
                message.reply_to = Email(reply_to)

            if config.get("SENDGRID_SANDBOX_MODE"):
                message.mail_settings = {
                    "sandbox_mode": {"enable": True}
                }

            sg = SendGridAPIClient(config["SENDGRID_API_KEY"])
            sg.send(message)

            return True

        except Exception as e:
            current_app.logger.error(f"SendGrid error: {e}")
            return False

    # -----------------------
    # SMTP fallback
    # -----------------------
    if config.get("SMTP_HOST"):
        try:
            msg = EmailMessage()
            msg["From"] = config.get("SMTP_FROM") or config.get("SMTP_USERNAME") or ""
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.set_content(body or "")

            with smtplib.SMTP(
                config["SMTP_HOST"],
                config.get("SMTP_PORT", 587),
                timeout=15
            ) as server:

                if config.get("SMTP_USE_TLS", True):
                    server.starttls()

                if config.get("SMTP_USERNAME"):
                    server.login(
                        config["SMTP_USERNAME"],
                        config["SMTP_PASSWORD"]
                    )

                server.send_message(msg)

            return True

        except Exception as e:
            current_app.logger.error(f"SMTP error: {e}")
            return False

    current_app.logger.warning("Email not sent: no email provider configured (SENDGRID_API_KEY or SMTP_HOST missing).")
    return False
