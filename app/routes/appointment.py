"""Appointment booking API routes."""

from typing import Annotated, Union

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse

from app.models.appointment import (
    AppointmentErrorResponse,
    AppointmentRequest,
    AppointmentSuccessResponse,
)
from app.services.appointment_service import (
    AppointmentService,
    get_appointment_service,
    get_request_logger,
)
from app.services.email_service import EmailServiceError
from app.services.google_sheet_service import GoogleSheetServiceError
from app.utils.validators import ValidationError

router = APIRouter(tags=["Appointments"])


@router.post(
    "/book-appointment",
    response_model=Union[AppointmentSuccessResponse, AppointmentErrorResponse],
    summary="Book a dental appointment",
    description=(
        "Receives appointment booking requests from RetellAI voice agent webhook. "
        "Validates input, saves to Google Sheets, and sends confirmation email."
    ),
    responses={
        200: {"model": AppointmentSuccessResponse},
        400: {"model": AppointmentErrorResponse},
        502: {"model": AppointmentErrorResponse},
        503: {"model": AppointmentErrorResponse},
        500: {"model": AppointmentErrorResponse},
    },
)
async def book_appointment(
    payload: AppointmentRequest,
    request: Request,
    service: Annotated[AppointmentService, Depends(get_appointment_service)],
) -> JSONResponse:
    """
    Book a new dental clinic appointment.

    Accepts customer details, validates business rules, persists to Google Sheets,
    and sends a confirmation email to the customer.
    """
    log = get_request_logger(request)

    try:
        result = service.book_appointment(payload)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=result.model_dump(exclude_none=True),
        )
    except ValidationError as exc:
        log.error("Validation Failed | reason=%s", exc.message)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=AppointmentErrorResponse(message=exc.message).model_dump(),
        )
    except GoogleSheetServiceError as exc:
        log.error("Google API Failed | reason=%s", exc.message)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=AppointmentErrorResponse(message=exc.message).model_dump(),
        )
    except EmailServiceError as exc:
        log.error("SMTP Error | reason=%s", exc.message)
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content=AppointmentErrorResponse(message=exc.message).model_dump(),
        )
    except Exception as exc:
        log.exception("Unexpected error during booking: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=AppointmentErrorResponse(
                message="An unexpected error occurred. Please try again later."
            ).model_dump(),
        )
