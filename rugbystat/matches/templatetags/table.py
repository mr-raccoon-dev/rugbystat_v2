from django import template

register = template.Library()

@register.filter()
def table(value):
    return value if value is not None else '-'
