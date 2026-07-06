"""Pydantic models for appointment booking."""

from datetime import date, datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AppointmentRequest(BaseModel):
    """
    Incoming appointment booking request.

    Supports both direct API field names and RetellAI webhook aliases.
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Customer full name",
        alias="customer_name",
    )
    phone: str = Field(..., description="10-digit phone number")
    email: str = Field(..., description="Customer email address")
    service: str = Field(
        ...,
        description="Dental treatment or service",
        alias="treatment",
    )
    date: str = Field(
        ...,
        description="Appointment date (YYYY-MM-DD)",
        alias="appointment_date",
    )
    time: str = Field(
        ...,
        description="Appointment time (e.g., 11:00 AM)",
        alias="appointment_time",
    )

    @field_validator("name", "phone", "email", "service", "date", "time", mode="before")
    @classmethod
    def strip_strings(cls, value: object) -> object:
        """Strip whitespace from string fields."""
        if isinstance(value, str):
            return value.strip()
        return value


class AppointmentRecord(BaseModel):
    """Internal representation of a confirmed appointment."""

    appointment_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    name: str
    phone: str
    email: str
    service: str
    appointment_date: date
    appointment_time: str


class AppointmentSuccessResponse(BaseModel):
    """Successful booking response returned to RetellAI."""

    status: Literal["success"] = "success"
    message: str = "Appointment booked successfully."

    appointment_id: str
    customer_name: str
    email: str
    service: str
    appointment_date: str
    appointment_time: str
    timestamp: str


class AppointmentErrorResponse(BaseModel):
    """Error response returned to RetellAI."""

    status: Literal["error"] = "error"
    message: str


class HealthResponse(BaseModel):
    """Health check endpoint response."""

    status: str = "healthy"
    service: str
    version: str
    timestamp: str
