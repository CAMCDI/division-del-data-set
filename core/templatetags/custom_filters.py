from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Custom filter para acceder a diccionarios en templates"""
    return dictionary.get(key, 0)