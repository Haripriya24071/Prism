"""Root main.py entrypoint for cloud hosting services (Render/Railway/Koyeb)."""
import os
import sys
from pathlib import Path

_current_dir = Path(__file__).resolve().parent
_backend_dir = _current_dir / "backend"
for _p in (str(_current_dir), str(_backend_dir)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from backend.main import app
