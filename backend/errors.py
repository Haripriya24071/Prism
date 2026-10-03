"""backend/errors.py — Custom exception classes for PRISM backend."""


class PrismException(Exception):
    """Base exception class for all PRISM errors."""

    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class InvalidSessionIdError(PrismException):
    """Raised when a session ID fails UUID v4 format validation."""

    def __init__(self, session_id: str):
        super().__init__(
            message=f"Invalid session ID format: '{session_id}'. Must be valid UUID v4.",
            status_code=400,
        )


class MimeTypeValidationError(PrismException):
    """Raised when an uploaded file fails MIME type validation via magic bytes."""

    def __init__(self, mime_type: str):
        super().__init__(
            message=f"Unsupported file MIME type: '{mime_type}'.",
            status_code=415,
        )


class KeyExhaustedError(PrismException):
    """Raised when all Gemini API keys in the key pool have hit rate limits."""

    def __init__(self):
        super().__init__(
            message="All Gemini API keys in the pool have been exhausted or rate limited.",
            status_code=429,
        )


class AgentExecutionError(PrismException):
    """Raised when a swarm agent fails to execute or returns invalid output."""

    def __init__(self, agent_name: str, detail: str):
        super().__init__(
            message=f"Swarm agent '{agent_name}' failed: {detail}",
            status_code=502,
        )


class ContextHarvestError(PrismException):
    """Raised when context harvester fails across critical sources."""

    def __init__(self, source: str, detail: str):
        super().__init__(
            message=f"Context harvest failed for source '{source}': {detail}",
            status_code=502,
        )


class EvaluationError(PrismException):
    """Raised when the evaluator or merge engine fails."""

    def __init__(self, detail: str):
        super().__init__(
            message=f"BRD evaluation or merge failed: {detail}",
            status_code=500,
        )
