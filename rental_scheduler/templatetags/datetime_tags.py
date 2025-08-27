from django import template
from django.utils import timezone

register = template.Library()


@register.filter(name='local_dt')
def local_dt(value, fmt='%m/%d/%Y %I:%M %p'):
    """Template filter to format a datetime value in local timezone."""
    if not value:
        return ''
    return timezone.localtime(value).strftime(fmt)
