from __future__ import annotations

from pathlib import Path
from fastapi.templating import Jinja2Templates

# Ordner: /srv/app/templates (im Container), lokal: app/templates
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
