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


# Context harvester
class ContextHarvestError(PRISMError):
    def __init__(self, message: str, detail: str | None = None):
        super().__init__(message, status_code=503, detail=detail)


# Swarm
class SwarmError(PRISMError):
    def __init__(self, message: str, detail: str | None = None):
        super().__init__(message, status_code=500, detail=detail)


class AgentTimeoutError(SwarmError):
    """Single agent exceeded its allowed time."""

    pass


# Evaluation + merge
class EvaluationError(PRISMError):
    def __init__(self, message: str, detail: str | None = None):
        super().__init__(message, status_code=500, detail=detail)


class MergeError(PRISMError):
    def __init__(self, message: str, detail: str | None = None):
        super().__init__(message, status_code=500, detail=detail)


# Session
class SessionNotFoundError(PRISMError):
    def __init__(self, session_id: str):
        super().__init__("Session not found", status_code=404, detail=f"id={session_id}")


class SessionExpiredError(PRISMError):
    def __init__(self, session_id: str):
        super().__init__("Session expired", status_code=410, detail=f"id={session_id}")


# GCP Storage
class StorageError(PRISMError):
    def __init__(self, message: str, detail: str | None = None):
        super().__init__(message, status_code=503, detail=detail)


# Alias for backward compatibility
PrismException = PRISMError
