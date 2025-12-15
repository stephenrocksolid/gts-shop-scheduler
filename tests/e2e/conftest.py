"""
Playwright E2E test configuration.
Provides fixtures for browser testing with Django.

For e2e tests, we test against an already-running dev server to avoid
async/sync conflicts between Playwright and Django's database operations.

Usage:
    1. Start the dev server: python manage.py runserver
    2. Run tests: DJANGO_ALLOW_ASYNC_UNSAFE=true pytest tests/e2e/ -v

Or use BASE_URL to specify a different server:
    BASE_URL=http://localhost:8000 pytest tests/e2e/ -v
"""
import os
import pytest


@pytest.fixture(scope="session")
def server_url():
    """
    Provide server URL for e2e tests.
    
    Uses BASE_URL environment variable or defaults to localhost:8000.
    Expects the Django dev server to already be running.
    """
    return os.environ.get("BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture(scope="function")
def page(browser):
    """Provide a new page for each test."""
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080}
    )
    page = context.new_page()
    yield page
    page.close()
    context.close()

