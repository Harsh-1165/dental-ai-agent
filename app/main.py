"""FastAPI application entry point."""

import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Callable

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.models.appointment import AppointmentErrorResponse
from app.routes import appointment, health
from app.utils.logger import setup_logging

settings = get_settings()
setup_logging(settings.log_level)
logger = logging.getLogger("dental_ai_agent.main")


def create_app() -> FastAPI:
    """Application factory for FastAPI instance."""
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Production-ready backend for QuensultingAI Dental Clinic AI Receptionist. "
            "Integrates with RetellAI Conversational Flow via webhooks to book "
            "appointments, persist data to Google Sheets, and send confirmation emails."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.middleware("http")
    async def request_context_middleware(
        request: Request,
        call_next: Callable,
    ):
        """Attach request ID, log requests, and measure response time."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start_time = time.perf_counter()

        logger.info(
            "Request Started | method=%s path=%s",
            request.method,
            request.url.path,
            extra={"request_id": request_id},
        )

        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.2f}"

        logger.info(
            "Request Completed | method=%s path=%s status=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
            extra={"request_id": request_id},
        )
        return response

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Convert Pydantic validation errors to consistent API responses."""
        errors = exc.errors()
        messages = []
        for error in errors:
            field = ".".join(str(loc) for loc in error.get("loc", []) if loc != "body")
            msg = error.get("msg", "Invalid value")
            messages.append(f"{field}: {msg}" if field else msg)

        message = "; ".join(messages) if messages else "Invalid request payload."
        request_id = getattr(request.state, "request_id", "-")
        logger.error(
            "Validation Failed | reason=%s",
            message,
            extra={"request_id": request_id},
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=AppointmentErrorResponse(message=message).model_dump(),
        )

    @application.exception_handler(Exception)
    async def global_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Catch unhandled exceptions and return safe error responses."""
        request_id = getattr(request.state, "request_id", "-")
        logger.exception(
            "Unexpected Exception | error=%s",
            exc,
            extra={"request_id": request_id},
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=AppointmentErrorResponse(
                message="An unexpected error occurred. Please try again later."
            ).model_dump(),
        )

    application.include_router(health.router, prefix="/api")
    application.include_router(appointment.router)

    @application.get("/", include_in_schema=False)
    async def root() -> dict:
        """Root endpoint with API metadata."""
        return {
            "service": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/api/health",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    return application


app = create_app()
