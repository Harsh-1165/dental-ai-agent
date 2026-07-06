"""Unit tests for appointment field validators."""

from datetime import date, timedelta

import pytest

from app.config import Settings
from app.utils.validators import (
    ValidationError,
    validate_appointment_fields,
    validate_email,
    validate_phone,
    parse_appointment_date,
    parse_appointment_time,
    validate_working_hours,
)


@pytest.fixture
def settings() -> Settings:
    return Settings()


class TestPhoneValidation:
    def test_valid_phone(self) -> None:
        assert validate_phone("9876543210") == "9876543210"

    def test_phone_with_spaces_and_dashes(self) -> None:
        assert validate_phone("987-654-3210") == "9876543210"

    def test_invalid_phone_too_short(self) -> None:
        with pytest.raises(ValidationError, match="10 digits"):
            validate_phone("987654321")

    def test_invalid_phone_letters(self) -> None:
        with pytest.raises(ValidationError):
            validate_phone("987654321a")


class TestEmailValidation:
    def test_valid_email(self) -> None:
        assert validate_email("Harsh@gmail.com") == "harsh@gmail.com"

    def test_invalid_email(self) -> None:
        with pytest.raises(ValidationError, match="Invalid email"):
            validate_email("not-an-email")


class TestDateValidation:
    def test_valid_future_weekday(self) -> None:
        future = date.today() + timedelta(days=1)
        while future.weekday() == 6:
            future += timedelta(days=1)
        result = parse_appointment_date(future.isoformat())
        assert result == future

    def test_past_date_rejected(self) -> None:
        past = date.today() - timedelta(days=1)
        with pytest.raises(ValidationError, match="past"):
            parse_appointment_date(past.isoformat())

    def test_sunday_rejected(self) -> None:
        future = date.today() + timedelta(days=1)
        while future.weekday() != 6:
            future += timedelta(days=1)
        with pytest.raises(ValidationError, match="Sunday"):
            parse_appointment_date(future.isoformat())


class TestTimeValidation:
    def test_valid_am_time(self) -> None:
        result = parse_appointment_time("11:00 AM")
        assert result.hour == 11

    def test_valid_pm_time(self) -> None:
        result = parse_appointment_time("3:30 PM")
        assert result.hour == 15

    def test_invalid_time_format(self) -> None:
        with pytest.raises(ValidationError):
            parse_appointment_time("25:99")


class TestWorkingHours:
    def test_within_hours(self, settings: Settings) -> None:
        validate_working_hours(parse_appointment_time("10:00 AM"), settings)

    def test_before_open(self, settings: Settings) -> None:
        with pytest.raises(ValidationError, match="9:00 AM"):
            validate_working_hours(parse_appointment_time("8:00 AM"), settings)

    def test_after_close(self, settings: Settings) -> None:
        with pytest.raises(ValidationError, match="6:00 PM"):
            validate_working_hours(parse_appointment_time("7:00 PM"), settings)


class TestFullValidation:
    def test_valid_appointment(self, settings: Settings) -> None:
        future = date.today() + timedelta(days=2)
        while future.weekday() == 6:
            future += timedelta(days=1)

        result = validate_appointment_fields(
            name="Harsh Maniya",
            phone="9876543210",
            email="harsh@gmail.com",
            service="Dental Cleaning",
            date_str=future.isoformat(),
            time_str="11:00 AM",
            settings=settings,
        )
        assert result[0] == "Harsh Maniya"
        assert result[3] == "Dental Cleaning"

    def test_invalid_service(self, settings: Settings) -> None:
        future = date.today() + timedelta(days=2)
        while future.weekday() == 6:
            future += timedelta(days=1)

        with pytest.raises(ValidationError, match="Invalid service"):
            validate_appointment_fields(
                name="Harsh Maniya",
                phone="9876543210",
                email="harsh@gmail.com",
                service="Unknown Service",
                date_str=future.isoformat(),
                time_str="11:00 AM",
                settings=settings,
            )
