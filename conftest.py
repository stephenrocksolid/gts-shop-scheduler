"""
pytest configuration for rental_scheduler tests.
"""
import pytest
import django
from django.conf import settings


def pytest_configure():
    """Configure Django settings for pytest."""
    # Django setup is handled by pytest-django via DJANGO_SETTINGS_MODULE in pytest.ini
    pass


@pytest.fixture
def api_client():
    """Return a Django test client."""
    from django.test import Client
    return Client()


@pytest.fixture
def calendar(db):
    """Create a test calendar."""
    from rental_scheduler.models import Calendar
    return Calendar.objects.create(
        name="Test Calendar",
        color="#3B82F6",
        is_active=True
    )


@pytest.fixture
def job(db, calendar):
    """Create a test job with valid dates."""
    from rental_scheduler.models import Job
    from django.utils import timezone
    from datetime import timedelta
    
    now = timezone.now()
    return Job.objects.create(
        calendar=calendar,
        business_name="Test Business",
        contact_name="Test Contact",
        phone="555-1234",
        start_dt=now,
        end_dt=now + timedelta(hours=2),
        all_day=False,
        status='uncompleted'
    )

