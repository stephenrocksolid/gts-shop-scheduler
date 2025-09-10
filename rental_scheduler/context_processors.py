"""
Context processors for rental_scheduler app.
These make data available to all templates globally.
"""

from .models import Calendar


def calendars(request):
    """
    Add active calendars to all template contexts.
    This makes the calendars available in the navigation dropdown.
    """
    return {
        'global_calendars': Calendar.objects.filter(is_active=True).order_by('name')
    }
