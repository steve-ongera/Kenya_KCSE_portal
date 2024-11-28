# myapp/templatetags/marks_filters.py
from django import template

register = template.Library()

@register.filter
def get(value, arg):
    """Custom filter to get a dictionary key."""
    return value.get(arg)
