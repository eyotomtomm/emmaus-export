"""Passenger entry point for cPanel's "Setup Python App".

cPanel/Passenger imports the name `application` from this file. It must live at
the application root and be named as the "Application startup file" in the
Python App UI.

The extra sys.path entry mirrors config/wsgi.py: the Django apps live in
emmaus/ but are imported unprefixed (e.g. `from pages.views import ...`), so
that directory has to be importable too.
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent
for path in (BASE_DIR, BASE_DIR / "emmaus"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.cpanel")

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
