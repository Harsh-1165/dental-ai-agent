"""Appointment booking business logic."""

import logging
from datetime import datetime
from typing import Annotated

from fastapi import Depends, Request

from app.config import Settings, get_settings
from app.models.appointment import (
    AppointmentErrorResponse,
    AppointmentRecord,
    AppointmentRequest,
    AppointmentSuccessResponse,
)
from app.services.email_service import EmailService, EmailServiceError, get_email_service
from app.services.google_sheet_service import (
    GoogleSheetService,
    GoogleSheetServiceError,
    get_google_sheet_service,
)
from app.utils.validators import ValidationError, validate_appointment_fields


class AppointmentService:
    """Orchestrates validation, persistence, and notification for bookings."""

    def __init__(
        self,
        settings: Settings,
        sheet_service: GoogleSheetService,
        email_service: EmailService,
        logger: logging.Logger,
    ) -> None:
        self._settings = settings
        self._sheet_service = sheet_service
        self._email_service = email_service
        self._logger = logger

    def book_appointment(
        self,
        request: AppointmentRequest,
    ) -> AppointmentSuccessResponse:
        """
        Validate, persist, and confirm an appointment booking.

        Args:
            request: Incoming appointment request payload.

        Returns:
            Success response with appointment metadata.

        Raises:
            ValidationError: When input validation fails.
            GoogleSheetServiceError: When Google Sheets persistence fails.
            EmailServiceError: When email delivery fails after save.
        """
        self._logger.info(
            "Appointment Received | name=%s service=%s date=%s time=%s",
            request.name,
            request.service,
            request.date,
            request.time,
        )

        (
            name,
            phone,
            email,
            service,
            appointment_date,
            _parsed_time,
            display_time,
        ) = validate_appointment_fields(
            name=request.name,
            phone=request.phone,
            email=request.email,
            service=request.service,
            date_str=request.date,
            time_str=request.time,
            settings=self._settings,
        )

        self._logger.info("Validation Passed | phone=%s email=%s", phone, email)

        record = AppointmentRecord(
            name=name,
            phone=phone,
            email=email,
            service=service,
            appointment_date=appointment_date,
            appointment_time=display_time,
        )

        self._sheet_service.append_appointment(record)
        self._email_service.send_confirmation(record)

        return AppointmentSuccessResponse(
            appointment_id=record.appointment_id,
            customer_name=record.name,
            email=record.email,
            service=record.service,
            appointment_date=str(record.appointment_date),
            appointment_time=record.appointment_time,
            timestamp=record.timestamp.isoformat() + "Z",
        )


def get_request_logger(request: Request) -> logging.Logger:
    """Provide a request-scoped logger with correlation ID."""
    request_id = getattr(request.state, "request_id", "-")
    return logging.getLogger(f"dental_ai_agent.appointment.{request_id}")


def get_appointment_service(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    sheet_service: Annotated[GoogleSheetService, Depends(get_google_sheet_service)],
    email_service: Annotated[EmailService, Depends(get_email_service)],
) -> AppointmentService:
    """Build AppointmentService with injected dependencies."""
    logger = get_request_logger(request)
    return AppointmentService(
        settings=settings,
        sheet_service=sheet_service,
        email_service=email_service,
        logger=logger,
    )
