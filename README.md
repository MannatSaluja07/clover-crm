# Clover CRM

A small CRM built in Django, with GDPR-aware data handling (consent
tracking, audit logging, export and erasure) as its core differentiator.
See `COMPLIANCE.md` for the data protection write-up.

## Local setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py migrate

# 4. Create an admin user (for /admin/)
python manage.py createsuperuser

# 5. Load sample data (contacts, deals, consent history)
python manage.py seed_data

# 6. Run the server
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` for the CRM, and `http://127.0.0.1:8000/admin/`
for the Django admin (also doubles as your audit log viewer).

## What's included

- `crm/models.py` — Contact, Deal, Activity, ConsentLog, AuditLog
- `crm/views.py` — dashboard, contact list/detail, deals, plus the GDPR
  export/erase actions
- `crm/templates/crm/` — Tailwind-styled templates (via CDN for now — see
  "Next steps" below)
- `crm/management/commands/seed_data.py` — sample data for demos

## Next steps toward a production-grade build

- Swap the Tailwind CDN `<script>` tag for a proper build (django-tailwind
  or a Vite/PostCSS pipeline) before deploying
- Move `SECRET_KEY` and database credentials to environment variables
- Point `DATABASES` at PostgreSQL (RDS) instead of SQLite
- Add a SonarQube scan alongside the existing CI checks
- Containerise with Docker and deploy to EC2 behind an ALB, DB in a
  private subnet — see `COMPLIANCE.md` for the infra-level items to add
  alongside it

## CI

Every push to `main` runs via GitHub Actions (`.github/workflows/ci.yml`):
lint (`ruff`), the Django test suite (`pytest`, covering auth, roles, and
the GDPR export/erase actions), and a dependency vulnerability check
(`pip-audit`).

Run the same checks locally before pushing:

```bash
pip install -r requirements-dev.txt
ruff check .
pytest -v
```

