from django import template

register = template.Library()

@register.inclusion_tag('rental_scheduler/components/button.html')
def primary_button(text, type="submit", extra_classes=""):
    return {
        'text': text,
        'type': type,
        'extra_classes': extra_classes
    } 