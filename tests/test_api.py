"""API integration tests for health and validation endpoints."""

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _next_weekday() -> str:
    future = date.today() + timedelta(days=2)
    while future.weekday() == 6:
        future += timedelta(days=1)
    return future.isoformat()


class TestHealthEndpoint:
    def test_health_returns_200(self) -> None:
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "X-Request-ID" in response.headers
        assert "X-Response-Time-Ms" in response.headers


class TestBookAppointmentValidation:
    def test_missing_fields_returns_422(self) -> None:
        response = client.post("/book-appointment", json={})
        assert response.status_code == 422
        assert response.json()["status"] == "error"

    def test_invalid_phone_returns_400(self) -> None:
        response = client.post(
            "/book-appointment",
            json={
                "name": "Harsh Maniya",
                "phone": "123",
                "email": "harsh@gmail.com",
                "service": "Dental Cleaning",
                "date": _next_weekday(),
                "time": "11:00 AM",
            },
        )
        assert response.status_code == 400
        assert response.json()["status"] == "error"

    def test_sunday_returns_400(self) -> None:
        future = date.today() + timedelta(days=1)
        while future.weekday() != 6:
            future += timedelta(days=1)

        response = client.post(
            "/book-appointment",
            json={
                "name": "Harsh Maniya",
                "phone": "9876543210",
                "email": "harsh@gmail.com",
                "service": "Dental Cleaning",
                "date": future.isoformat(),
                "time": "11:00 AM",
            },
        )
        assert response.status_code == 400
        assert "Sunday" in response.json()["message"]

    def test_retellai_field_aliases(self) -> None:
        response = client.post(
            "/book-appointment",
            json={
                "customer_name": "Harsh Maniya",
                "phone": "9876543210",
                "email": "harsh@gmail.com",
                "treatment": "Dental Cleaning",
                "appointment_date": _next_weekday(),
                "appointment_time": "11:00 AM",
            },
        )
        assert response.status_code in (200, 502, 503)
