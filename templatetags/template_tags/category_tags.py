from django import template

register = template.Library()

@register.simple_tag
def get_color_for_category(category):
    category_colors = {
        'Category1': 'red',
        'Category2': 'blue',
        'Category3': 'green',
        # Add more mappings as needed
    }
    return category_colors.get(category, 'defaultColor')  # Fallback color
