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
- Add a SonarQube scan alongside the existing CI checks (done — see
  SonarCloud badge above)
- Put the EC2 instance behind an Application Load Balancer with a TLS
  certificate, and move the database into a private subnet (currently the
  Postgres container runs alongside the app on the same instance for
  simplicity)

## Deployment (Docker + PostgreSQL + AWS EC2)

The app is containerised and runs with PostgreSQL instead of SQLite in
this configuration. See `terraform/README.md` for provisioning the EC2
instance, and the steps below for deploying onto it once it exists.

**Run it locally with Docker first** (recommended before deploying):

```bash
cp .env.example .env
# edit .env and set real values for DB_PASSWORD and DJANGO_SECRET_KEY
docker compose up --build
```

Visit `http://localhost:8000/`. This runs the exact same containers that
go on EC2, so if it works here, it'll work there.

**Deploying to EC2:**

1. Provision the instance with Terraform — see `terraform/README.md`
2. SSH into the instance (Terraform prints the command)
3. Clone the repo onto the instance:
   ```bash
   git clone https://github.com/MannatSaluja07/clover-crm.git
   cd clover-crm
   cp .env.example .env
   nano .env   # set real DB_PASSWORD and DJANGO_SECRET_KEY
   ```
4. Start the containers:
   ```bash
   sudo docker compose up --build -d
   ```
5. Create a superuser and load demo data:
   ```bash
   sudo docker compose exec web python manage.py createsuperuser
   sudo docker compose exec web python manage.py seed_data
   ```
6. Visit `http://<instance-public-ip>:8000/`

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

