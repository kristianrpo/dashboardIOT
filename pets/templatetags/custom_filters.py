from django import template

register = template.Library()

@register.filter
def format_time(task):
    print(task)
    hour = task["hour"] if task["hour"] is not None else 0
    minute = task["minute"] if task["minute"] is not None else 0
    return f"{hour:02d}:{minute:02d}"