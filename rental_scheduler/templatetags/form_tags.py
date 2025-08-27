from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='addclass')
def addclass(field, css):
    if hasattr(field, 'as_widget'):
        return field.as_widget(attrs={'class': css})
    return field

@register.filter(name='addattr')
def addattr(field, attr):
    """
    Add an attribute to a form field.
    Usage: {{ field|addattr:"data-price:100" }}
    """
    if not hasattr(field, 'as_widget'):
        return field
        
    attrs = {}
    if ':' in attr:
        key, value = attr.split(':')
        attrs[key] = value
    return field.as_widget(attrs=attrs)

@register.filter(name='addattrs')
def addattrs(field, attrs_str):
    """
    Add multiple attributes to a form field.
    Usage: {{ field|addattrs:"data-price:100,data-tax-rate:8.25" }}
    """
    if not hasattr(field, 'as_widget'):
        return field
        
    attrs = {}
    for attr in attrs_str.split(','):
        if ':' in attr:
            key, value = attr.split(':')
            attrs[key] = value
    return field.as_widget(attrs=attrs)

@register.filter(name='equals')
def equals(value1, value2):
    """
    Compare two values for equality, handling type conversion.
    Usage: {{ current_category|equals:category.id }}
    """
    try:
        # Try to convert both to strings for comparison
        return str(value1) == str(value2)
    except:
        return False 