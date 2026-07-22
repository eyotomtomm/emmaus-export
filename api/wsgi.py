"""Vercel serverless entry point for Django."""

import os
import sys
from pathlib import Path

# Vercel runs this from /vercel/path0/api/wsgi.py
# Project root is one level up
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(BASE_DIR / "emmaus") not in sys.path:
    sys.path.insert(0, str(BASE_DIR / "emmaus"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.vercel")

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
