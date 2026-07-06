"""SMTP email service for appointment confirmations."""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Annotated, Optional

from fastapi import Depends

from app.config import Settings, get_settings
from app.models.appointment import AppointmentRecord


class EmailServiceError(Exception):
    """Raised when email delivery fails."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class EmailService:
    """Service for sending appointment confirmation emails via Gmail SMTP."""

    def __init__(self, settings: Settings, logger: Optional[logging.Logger] = None) -> None:
        self._settings = settings
        self._logger = logger or logging.getLogger("dental_ai_agent.email")

    def _validate_smtp_config(self) -> None:
        """Ensure required SMTP environment variables are set."""
        missing = []
        if not self._settings.smtp_username:
            missing.append("SMTP_USERNAME")
        if not self._settings.smtp_password:
            missing.append("SMTP_PASSWORD")
        if not self._settings.smtp_from_email:
            missing.append("SMTP_FROM_EMAIL")

        if missing:
            raise EmailServiceError(
                f"SMTP configuration incomplete. Missing: {', '.join(missing)}."
            )

    def _build_message(self, appointment: AppointmentRecord) -> MIMEMultipart:
        """Construct the confirmation email message."""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Appointment Confirmed"
        msg["From"] = self._settings.smtp_from_email
        msg["To"] = appointment.email

        plain_body = (
            f"Hello {appointment.name},\n\n"
            f"Your appointment has been confirmed.\n\n"
            f"Appointment ID: {appointment.appointment_id}\n"
            f"Treatment: {appointment.service}\n"
            f"Date: {appointment.appointment_date.strftime('%A, %B %d, %Y')}\n"
            f"Time: {appointment.appointment_time}\n\n"
            f"Thank you for choosing {self._settings.clinic_name}.\n"
        )

        html_body = (
            f"<html><body>"
            f"<p>Hello <strong>{appointment.name}</strong>,</p>"
            f"<p>Your appointment has been confirmed.</p>"
            f"<ul>"
            f"<li><strong>Appointment ID:</strong> {appointment.appointment_id}</li>"
            f"<li><strong>Treatment:</strong> {appointment.service}</li>"
            f"<li><strong>Date:</strong> "
            f"{appointment.appointment_date.strftime('%A, %B %d, %Y')}</li>"
            f"<li><strong>Time:</strong> {appointment.appointment_time}</li>"
            f"</ul>"
            f"<p>Thank you for choosing {self._settings.clinic_name}.</p>"
            f"</body></html>"
        )

        msg.attach(MIMEText(plain_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))
        return msg

    def send_confirmation(self, appointment: AppointmentRecord) -> None:
        """
        Send appointment confirmation email to the customer.

        Args:
            appointment: Confirmed appointment details.

        Raises:
            EmailServiceError: On SMTP or configuration failures.
        """
        self._validate_smtp_config()
        message = self._build_message(appointment)

        try:
            with smtplib.SMTP(
                self._settings.smtp_host,
                self._settings.smtp_port,
                timeout=30,
            ) as server:
                if self._settings.smtp_use_tls:
                    server.starttls()
                server.login(
                    self._settings.smtp_username,
                    self._settings.smtp_password,
                )
                server.sendmail(
                    self._settings.smtp_from_email,
                    [appointment.email],
                    message.as_string(),
                )

            self._logger.info(
                "Email Sent | appointment_id=%s recipient=%s",
                appointment.appointment_id,
                appointment.email,
            )
        except smtplib.SMTPException as exc:
            self._logger.error("SMTP Error | error=%s", exc)
            raise EmailServiceError(
                "Failed to send confirmation email. Appointment was saved."
            ) from exc
        except OSError as exc:
            self._logger.error("SMTP Connection Error | error=%s", exc)
            raise EmailServiceError(
                "Could not connect to email server. Appointment was saved."
            ) from exc


def get_email_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> EmailService:
    """Factory for EmailService dependency injection."""
    return EmailService(settings=settings)
