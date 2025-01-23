
from django import template

register = template.Library()

@register.filter
def get_category_color(category_colors, category):
    return category_colors.get(category, 'defaultColor')
