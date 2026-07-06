"""Custom validation utilities for appointment booking."""

import re
from datetime import date, datetime, time
from typing import Optional, Tuple

from app.config import Settings

PHONE_PATTERN = re.compile(r"^\d{10}$")
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

TIME_FORMATS = (
    "%I:%M %p",
    "%I:%M%p",
    "%H:%M",
    "%H:%M:%S",
)


class ValidationError(Exception):
    """Raised when appointment data fails business validation."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def validate_phone(phone: str) -> str:
    """
    Validate phone number is exactly 10 digits.

    Args:
        phone: Raw phone string from request.

    Returns:
        Validated phone string.

    Raises:
        ValidationError: If phone format is invalid.
    """
    cleaned = phone.strip().replace("-", "").replace(" ", "")
    if not PHONE_PATTERN.match(cleaned):
        raise ValidationError(
            "Invalid phone number. Phone must be exactly 10 digits."
        )
    return cleaned


def validate_email(email: str) -> str:
    """
    Validate email address format.

    Args:
        email: Raw email string from request.

    Returns:
        Normalized email string.

    Raises:
        ValidationError: If email format is invalid.
    """
    normalized = email.strip().lower()
    if not EMAIL_PATTERN.match(normalized):
        raise ValidationError("Invalid email address format.")
    return normalized


def parse_appointment_date(date_str: str) -> date:
    """
    Parse and validate appointment date.

    Args:
        date_str: Date in YYYY-MM-DD format.

    Returns:
        Parsed date object.

    Raises:
        ValidationError: If date is invalid, in the past, or on Sunday.
    """
    try:
        parsed = datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValidationError(
            "Invalid date format. Use YYYY-MM-DD (e.g., 2026-07-10)."
        ) from exc

    today = date.today()
    if parsed < today:
        raise ValidationError("Appointment date cannot be in the past.")

    if parsed.weekday() == 6:
        raise ValidationError(
            "Appointments are not available on Sundays. "
            "Clinic is open Monday through Saturday."
        )

    return parsed


def parse_appointment_time(time_str: str) -> time:
    """
    Parse appointment time from various supported formats.

    Args:
        time_str: Time string (e.g., '11:00 AM', '14:30').

    Returns:
        Parsed time object.

    Raises:
        ValidationError: If time format is unrecognized.
    """
    normalized = time_str.strip().upper()
    for fmt in TIME_FORMATS:
        try:
            return datetime.strptime(normalized, fmt).time()
        except ValueError:
            continue

    raise ValidationError(
        "Invalid time format. Use formats like '11:00 AM' or '14:30'."
    )


def validate_working_hours(
    appointment_time: time,
    settings: Settings,
) -> None:
    """
    Ensure appointment time falls within clinic working hours.

    Args:
        appointment_time: Parsed appointment time.
        settings: Application settings with hour boundaries.

    Raises:
        ValidationError: If time is outside 9 AM – 6 PM.
    """
    start = time(settings.working_hour_start, 0)
    end = time(settings.working_hour_end, 0)

    if appointment_time < start or appointment_time > end:
        raise ValidationError(
            "Appointment time must be between 9:00 AM and 6:00 PM. "
            "Clinic is open Monday through Saturday, 9:00 AM – 6:00 PM."
        )


def validate_service(service: str, settings: Settings) -> str:
    """
    Validate treatment/service is offered by the clinic.

    Args:
        service: Requested treatment name.
        settings: Application settings with valid services list.

    Returns:
        Canonical service name.

    Raises:
        ValidationError: If service is not in the allowed list.
    """
    normalized = service.strip()
    valid_map = {s.lower(): s for s in settings.valid_services}

    match = valid_map.get(normalized.lower())
    if not match:
        allowed = ", ".join(settings.valid_services)
        raise ValidationError(
            f"Invalid service '{service}'. Available services: {allowed}."
        )
    return match


def validate_name(name: str) -> str:
    """
    Validate customer name is present and reasonable length.

    Args:
        name: Customer full name.

    Returns:
        Trimmed name string.

    Raises:
        ValidationError: If name is empty or too short.
    """
    trimmed = name.strip()
    if len(trimmed) < 2:
        raise ValidationError("Name must be at least 2 characters long.")
    if len(trimmed) > 100:
        raise ValidationError("Name must not exceed 100 characters.")
    return trimmed


def validate_appointment_fields(
    name: str,
    phone: str,
    email: str,
    service: str,
    date_str: str,
    time_str: str,
    settings: Settings,
) -> Tuple[str, str, str, str, date, time, str]:
    """
    Run all appointment field validations.

    Returns:
        Tuple of (name, phone, email, service, date, time, display_time).
    """
    validated_name = validate_name(name)
    validated_phone = validate_phone(phone)
    validated_email = validate_email(email)
    validated_service = validate_service(service, settings)
    validated_date = parse_appointment_date(date_str)
    parsed_time = parse_appointment_time(time_str)
    validate_working_hours(parsed_time, settings)

    display_time = parsed_time.strftime("%I:%M %p").lstrip("0")
    return (
        validated_name,
        validated_phone,
        validated_email,
        validated_service,
        validated_date,
        parsed_time,
        display_time,
    )
