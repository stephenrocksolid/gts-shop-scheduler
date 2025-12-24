# Local Development Runbook

Last updated: 2025-12-22

This runbook covers setting up and running the app locally (Django + Tailwind) and running tests.

## Prerequisites

- Python 3.x
- Node.js (recent LTS)

## Setup (first time)

### 1) Create a virtualenv + install Python deps

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2) Install frontend deps (Tailwind)

```bash
npm install
```

One-time build:

```bash
npm run build
```

Watch mode (recommended during UI work):

```bash
npm run watch
```

### 3) Create `.env`

Linux/macOS:

```bash
cp env_example.txt .env
```

Windows (PowerShell):

```powershell
Copy-Item .\env_example.txt .\.env
```

Common env vars:

- `SECRET_KEY`
- `TIME_ZONE` (defaults to `America/New_York`)
- `OPENAI_API_KEY` (optional)
- Optional PostgreSQL toggle:
  - set `DB_NAME` (and `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`) to enable Postgres in `gts_django/settings.py`

### 4) Migrate DB + create admin user

```bash
python manage.py migrate
python manage.py createsuperuser
```

## Run the app

Dev server:

```bash
python manage.py runserver
```

Then open `http://127.0.0.1:8000/`.

Production-style server (Waitress):

```bash
python serve.py
```

## Tests

### Unit/integration (pytest)

```bash
pytest
```

Coverage:

```bash
pytest --cov=rental_scheduler --cov-report=term-missing
```

### E2E (Playwright)

E2E tests expect a **running** Django server.

One-time browser install:

```bash
python -m playwright install
```

Terminal 1:

```bash
python manage.py runserver
```

Terminal 2 (Linux/macOS):

```bash
DJANGO_ALLOW_ASYNC_UNSAFE=true pytest tests/e2e -v
```

Terminal 2 (Windows PowerShell):

```powershell
$env:DJANGO_ALLOW_ASYNC_UNSAFE="true"
pytest tests/e2e -v
```

Optional: point E2E tests at a different base URL:

Linux/macOS:

```bash
BASE_URL="http://127.0.0.1:8000" pytest tests/e2e -v
```


