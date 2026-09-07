# Deploying to cPanel

The repo was originally wired for Vercel (`vercel.json`, `config/settings/vercel.py`).
This adds a cPanel path alongside it; nothing about the Vercel setup was removed.

## Before you start: does the package support Python?

Django cannot run on a cPanel package that only offers WordPress tooling. In
cPanel, look under **Software** for **Setup Python App**.

- **Present** → follow the steps below.
- **Absent** → the host has not enabled Passenger for this account. Ask them to
  enable "Setup Python App" (it is a standard cPanel/CloudLinux feature), or
  keep the site on Vercel and just point DNS there. Uploading these files
  without it will not make the site run.

## Steps

1. **Setup Python App** → Create Application
   - Python version: **3.12** (matches `.python-version`)
   - Application root: e.g. `emmaus-export`
   - Application URL: `emmausimportexport.com`
   - Application startup file: `passenger_wsgi.py`
   - Application entry point: `application`

2. **Upload the code** into the application root — Git Version Control in cPanel
   pointed at the repo, or File Manager upload. Do not upload `venv/`,
   `staticfiles/`, or `db.sqlite3` from your machine.

3. **Create `.env`** in the application root from `.env.example` and fill in
   `DJANGO_SECRET_KEY`. Generate one with:

   ```
   python -c "import secrets; print(secrets.token_urlsafe(64))"
   ```

4. **Install dependencies.** In the Python App UI, "Enter to the virtual
   environment" gives you a command to paste into Terminal, then:

   ```
   pip install -r requirements/cpanel.txt
   ```

   Use `requirements/cpanel.txt`, not `production.txt` — that one pulls Redis,
   gunicorn and S3 packages this host has no use for, and `hiredis` needs a C
   toolchain that shared accounts often lack.

5. **Migrate and collect static:**

   ```
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

   WhiteNoise serves `/static/` from the app, so no Apache alias or
   `public_html` symlink is needed.

6. **Restart** the app from the Python App UI after every deploy — Passenger
   caches the loaded application.

## Turn on HTTPS first

The domain currently shows a **self-signed certificate**, which browsers reject
with a full-page warning. In cPanel go to **Security → SSL/TLS Status**, select
the domain, and **Run AutoSSL** to get a free Let's Encrypt certificate.

Only once that shows as valid, set in `.env` and restart:

```
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SECURE_HSTS_SECONDS=60
```

Raise `DJANGO_SECURE_HSTS_SECONDS` to `518400` after confirming nothing broke.
It is left off by default deliberately: forcing the HTTPS redirect while the
certificate is still self-signed makes the site unreachable for real visitors.

## Notes

- `config/settings/cpanel.py` is the settings module. It differs from
  `production.py` only where shared hosting forces it: local-memory cache
  instead of Redis, SQLite on local disk, WhiteNoise instead of S3.
- Logs go to `logs/django.log` (rotating, 5 MB × 3) because Passenger discards
  stdout.
- SQLite is appropriate here — the public site is read-only brochure content.
  Move to the MySQL database cPanel provides if the site ever takes real writes.
