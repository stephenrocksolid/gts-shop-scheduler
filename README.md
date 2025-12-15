# GTS Shop Scheduler

A Django app for scheduling and managing shop/rental jobs. The UI uses TailwindCSS, and the calendar experience is driven by JavaScript in `rental_scheduler/static/`.

## Tech stack

- **Backend**: Django (`gts_django/`, app: `rental_scheduler/`)
- **Database**: SQLite by default (dev) + optional PostgreSQL
- **Frontend**: TailwindCSS (build/watch via npm)

## Prerequisites

- **Python**: 3.x
- **Node.js**: recent LTS recommended (needed for Tailwind builds)
- **Database**:
  - Default: **SQLite** (no extra setup)
  - Optional: PostgreSQL (if you choose to wire it up)

## Setup

### 1) Clone

```bash
git clone https://github.com/joshuarocksolid/gts-rental-scheduler.git
cd gts-shop-scheduler
```

### 2) Python venv + dependencies

```bash
# Windows (PowerShell)
python -m venv env
.\env\Scripts\Activate.ps1

pip install -r requirements.txt
```

### 3) Frontend deps + CSS build

```bash
npm install

# one-time build
npm run build

# watch during development
npm run watch
```

### 4) Environment variables

Copy the example env file and adjust as needed:

```bash
# Windows (PowerShell)
Copy-Item .\env_example.txt .\.env
```

Key env vars (see `env_example.txt`):
- **`SECRET_KEY`**: set for local dev
- **`TIME_ZONE`**: defaults to `America/New_York` if not set
- **`OPENAI_API_KEY`**: optional (used for AI parsing features)

### 5) Database setup (SQLite default)

```bash
python manage.py migrate
python manage.py createsuperuser
```

## Running the app

### Development (recommended)

```bash
python manage.py runserver
```

Then open `http://127.0.0.1:8000/`.

Keep Tailwind running in another terminal during UI work:

```bash
npm run watch
```

### Waitress (simple production-style run)

This repo includes `serve.py` which runs the WSGI app with Waitress on port 8000:

```bash
python serve.py
```

## Project structure (high level)

- `gts_django/`: Django project (settings/urls/wsgi)
- `rental_scheduler/`: main Django app (models/views/forms/templates/static)
- `rental_scheduler/tests/`: pytest-based Django/unit/integration tests
- `tests/e2e/`: Playwright E2E smoke tests (browser tests)
- `src/css/`: Tailwind input CSS
- `rental_scheduler/static/rental_scheduler/css/`: built CSS output

## Testing

This repo uses **pytest** (with `pytest-django`). By default, pytest will discover tests under:
- `rental_scheduler/tests/`
- `tests/` (includes `tests/e2e/`)

### Run unit/integration tests (pytest)

Run everything:

```bash
pytest
```

Run a single file:

```bash
pytest rental_scheduler/tests/test_job_phone_formatting.py -v
```

Run by keyword:

```bash
pytest -k phone -v
```

### Coverage

```bash
pytest --cov=rental_scheduler --cov-report=term-missing
```

### Run E2E (Playwright)

E2E tests live under `tests/e2e/` and are designed to run against an **already-running** Django server.

One-time browser install:

```bash
python -m playwright install
```

Terminal 1 (start the server):

```bash
python manage.py runserver
```

Terminal 2 (run E2E tests):

```bash
# PowerShell
$env:DJANGO_ALLOW_ASYNC_UNSAFE="true"
pytest tests/e2e -v
```

Optional: point E2E tests at a different server URL:

```bash
# PowerShell
$env:BASE_URL="http://127.0.0.1:8000"
pytest tests/e2e -v
```

Note: the E2E fixtures document the same approach in `tests/e2e/conftest.py`.

## Development notes

- **CSS**: Tailwind output is generated via `npm run build` / `npm run watch` (see `package.json`).
- **DB**: Defaults to SQLite (`db.sqlite3`). PostgreSQL is not enabled by default; if you enable it, update Django DB settings accordingly.

## Contributing

1. Create a feature branch
2. Make changes + add tests where appropriate
3. Open a pull request

## License

ISC License