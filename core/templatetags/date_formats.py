from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def timesince_date(value):
    if not value:
        return ''
    now = timezone.now()
    difference = now - value

    seconds = difference.total_seconds()
    minutes = seconds // 60
    hours = minutes // 60
    days = difference.days
    weeks = days // 7

    if weeks > 0:
        return f'{weeks:.0f} week{"s" if weeks > 1 else ""} ago'
    elif days > 0:
        return f'{days:.0f} day{"s" if days > 1 else ""} ago'
    elif hours > 0:
        return f'{hours:.0f} hour{"s" if hours > 1 else ""} ago'
    elif minutes > 0:
        return f'{minutes:.0f} minute{"s" if minutes > 1 else ""} ago'
    else:
        return 'just now'