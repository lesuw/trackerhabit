from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='min_filter')
def min_filter(value, arg):
    try:
        return min(int(value), int(arg))
    except (ValueError, TypeError):
        return value