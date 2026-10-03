"""backend/errors.py — Custom exception hierarchy for PRISM backend."""


class PRISMError(Exception):
    """Base for all PRISM exceptions. Carries HTTP status + safe public message."""

    def __init__(self, message: str, status_code: int = 500, detail: str | None = None):
        self.message = message  # shown to client — must be generic
        self.status_code = status_code
        self.detail = detail  # internal only — never returned in HTTP responses
        super().__init__(message)


# Intake
class IntakeError(PRISMError):
    def __init__(self, message: str, detail: str | None = None):
        super().__init__(message, status_code=422, detail=detail)


class InvalidFileError(IntakeError):
    """File fails MIME type or size validation."""

    pass
