"""Vercel serverless entry point for Django."""

import os
import sys
from pathlib import Path

# Add emmaus app directory to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "emmaus"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.vercel")

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
