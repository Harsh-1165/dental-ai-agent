"""Google Sheets integration for persisting appointments."""

import logging
from pathlib import Path
from typing import Annotated, List, Optional

from fastapi import Depends
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.config import Settings, get_settings
from app.models.appointment import AppointmentRecord

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
HEADER_ROW = [
    "Appointment ID",
    "Timestamp",
    "Name",
    "Phone",
    "Email",
    "Treatment",
    "Appointment Date",
    "Appointment Time",
]


class GoogleSheetServiceError(Exception):
    """Raised when Google Sheets API operations fail."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class GoogleSheetService:
    """Service for reading and writing appointment data to Google Sheets."""

    def __init__(self, settings: Settings, logger: Optional[logging.Logger] = None) -> None:
        self._settings = settings
        self._logger = logger or logging.getLogger("dental_ai_agent.google_sheets")
        self._service = None
        self._resolved_sheet_name: Optional[str] = None

    def _get_credentials(self) -> Credentials:
        """Load Google service account credentials from file."""
        credentials_path = Path(self._settings.google_credentials_path)
        if not credentials_path.exists():
            raise GoogleSheetServiceError(
                f"Google credentials file not found at '{credentials_path}'. "
                "Set GOOGLE_CREDENTIALS_PATH in your environment."
            )
        return Credentials.from_service_account_file(
            str(credentials_path),
            scopes=SCOPES,
        )

    def _get_service(self):
        """Lazy-initialize Google Sheets API client."""
        if self._service is None:
            credentials = self._get_credentials()
            self._service = build("sheets", "v4", credentials=credentials, cache_discovery=False)
        return self._service

    def _resolve_worksheet_name(self) -> str:
        """Resolve worksheet tab name, creating it if missing."""
        if self._resolved_sheet_name:
            return self._resolved_sheet_name

        if not self._settings.google_sheet_id:
            raise GoogleSheetServiceError(
                "GOOGLE_SHEET_ID is not configured. Set it in your environment."
            )

        service = self._get_service()
        target = self._settings.google_sheet_name

        try:
            metadata = service.spreadsheets().get(
                spreadsheetId=self._settings.google_sheet_id,
                fields="sheets.properties.title",
            ).execute()
        except HttpError as exc:
            raise GoogleSheetServiceError(
                f"Unable to access Google Spreadsheet: {exc}"
            ) from exc

        for sheet in metadata.get("sheets", []):
            title = sheet.get("properties", {}).get("title", "")
            if title == target:
                self._resolved_sheet_name = title
                return title

        try:
            service.spreadsheets().batchUpdate(
                spreadsheetId=self._settings.google_sheet_id,
                body={
                    "requests": [
                        {"addSheet": {"properties": {"title": target}}}
                    ]
                },
            ).execute()
            self._logger.info("Created worksheet '%s'", target)
            self._resolved_sheet_name = target
            return target
        except HttpError as exc:
            sheets = metadata.get("sheets", [])
            if sheets:
                fallback = sheets[0]["properties"]["title"]
                self._logger.warning(
                    "Worksheet '%s' not found. Using '%s' instead.",
                    target,
                    fallback,
                )
                self._resolved_sheet_name = fallback
                return fallback
            raise GoogleSheetServiceError(
                f"Spreadsheet has no worksheets and could not create '{target}': {exc}"
            ) from exc

    def _sheet_range(self, cell_range: str = "A1") -> str:
        """Build fully qualified A1 notation range for the configured sheet."""
        sheet_name = self._resolve_worksheet_name()
        return f"'{sheet_name}'!{cell_range}"

    def ensure_headers(self) -> None:
        """Create header row if the sheet is empty."""
        service = self._get_service()
        sheet = service.spreadsheets()

        try:
            result = sheet.values().get(
                spreadsheetId=self._settings.google_sheet_id,
                range=self._sheet_range("A1:H1"),
            ).execute()
            existing = result.get("values", [])
            if not existing:
                sheet.values().update(
                    spreadsheetId=self._settings.google_sheet_id,
                    range=self._sheet_range("A1:H1"),
                    valueInputOption="RAW",
                    body={"values": [HEADER_ROW]},
                ).execute()
                self._logger.info("Google Sheet header row created")
        except HttpError as exc:
            raise GoogleSheetServiceError(
                f"Failed to initialize Google Sheet headers: {exc}"
            ) from exc

    def append_appointment(self, appointment: AppointmentRecord) -> None:
        """
        Append a confirmed appointment row to Google Sheets.

        Args:
            appointment: Validated appointment record to persist.

        Raises:
            GoogleSheetServiceError: On API or configuration failures.
        """
        self.ensure_headers()

        row: List[str] = [
            appointment.appointment_id,
            appointment.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
            appointment.name,
            appointment.phone,
            appointment.email,
            appointment.service,
            appointment.appointment_date.isoformat(),
            appointment.appointment_time,
        ]

        service = self._get_service()
        try:
            service.spreadsheets().values().append(
                spreadsheetId=self._settings.google_sheet_id,
                range=self._sheet_range("A:H"),
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": [row]},
            ).execute()
            self._logger.info(
                "Google Sheet Updated | appointment_id=%s",
                appointment.appointment_id,
            )
        except HttpError as exc:
            self._logger.error("Google API Failed | error=%s", exc)
            raise GoogleSheetServiceError(
                "Failed to save appointment to Google Sheets. Please try again later."
            ) from exc


def get_google_sheet_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> GoogleSheetService:
    """Factory for GoogleSheetService dependency injection."""
    return GoogleSheetService(settings=settings)
