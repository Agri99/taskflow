import json
from django import template

register = template.Library()


@register.filter
def pprint(value):
    """Pretty print JSON data"""
    try:
        return json.dumps(value, indent=2, sort_keys=True)
    except (ValueError, TypeError):
        return str(value)