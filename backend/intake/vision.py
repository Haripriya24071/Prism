"""backend/intake/vision.py — Gemini Vision image analysis."""

from typing import TYPE_CHECKING
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

if TYPE_CHECKING:
    from backend.errors import IntakeError, InvalidFileError
    from backend.config import get_flash_model
else:
    try:
        from backend.errors import IntakeError, InvalidFileError
        from backend.config import get_flash_model
    except ImportError:
        from errors import IntakeError, InvalidFileError
        from config import get_flash_model

logger = structlog.get_logger()

# Magic bytes
_JPEG_MAGIC = b"\xff\xd8\xff"
_PNG_MAGIC = b"\x89PNG"
_MAX_SIZE = 10 * 1024 * 1024  # 10 MB

_VISION_SYSTEM_PROMPT = """You are PRISM's intake analyst.
Analyse this image and extract every detail relevant to a business idea:
- What product or service is depicted or implied
- Target audience visible or implied
- Market or industry context
- Any text, logos, or data visible in the image
- What problem this appears to solve
Return a clear, structured paragraph. Be specific. Do not hallucinate details not present."""


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
async def _call_vision(image_bytes: bytes, mime_type: str) -> str:
    """Inner function — retried by tenacity. Separated so retry decorator is clean."""
    from vertexai.generative_models import Part  # source-driven-development: correct import path

    model = get_flash_model()
    image_part = Part.from_data(data=image_bytes, mime_type=mime_type)
    response = model.generate_content([_VISION_SYSTEM_PROMPT, image_part])
    return response.text  # type: ignore[no-any-return]


async def analyse_image(image_bytes: bytes) -> str:
    """Gemini 2.0 Flash vision call via Vertex AI.

    Returns text description of the business idea present in the image. Raises InvalidFileError for
    wrong format/size, IntakeError on Gemini failure.
    """
    if len(image_bytes) == 0:
        raise InvalidFileError("Image file is empty")

    if len(image_bytes) > _MAX_SIZE:
        raise InvalidFileError("Image exceeds 10 MB limit")

    if image_bytes.startswith(_JPEG_MAGIC):
        mime_type = "image/jpeg"
    elif image_bytes.startswith(_PNG_MAGIC):
        mime_type = "image/png"
    else:
        raise InvalidFileError("Only JPEG and PNG images are accepted")

    logger.info("vision_analysis_start", mime_type=mime_type, size_bytes=len(image_bytes))

    try:
        result = await _call_vision(image_bytes, mime_type)
    except Exception as e:
        logger.error("vision_analysis_failed", error_type=type(e).__name__)
        raise IntakeError("Image analysis failed", detail=str(e))

    logger.info("vision_analysis_complete", response_chars=len(result))
    return result
