from django import template
import hashlib

register = template.Library()

@register.filter
def percentage(value, total):
    """
    Calculate the percentage of value compared to total.
    Returns 0 if total is 0 to avoid division by zero.
    """
    try:
        if total == 0:
            return 0
        return round((float(value) / float(total)) * 100, 1)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def subtract(value, arg):
    """Subtract the arg from the value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def multiply(value, arg):
    """Multiply the value by the arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def divide(value, arg):
    """Divide the value by the arg"""
    try:
        if arg == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0

@register.filter
def avatar_color(username):
    """Generate a consistent color code based on the username."""
    colors = [
        '#4CAF50', '#2196F3', '#9C27B0', '#FF5722', '#607D8B',
        '#673AB7', '#E91E63', '#3F51B5', '#00BCD4', '#FFC107'
    ]
    
    # Create a hash of the username to get a consistent color
    hash_object = hashlib.md5(username.encode())
    hash_value = int(hash_object.hexdigest(), 16)
    
    # Use modulo to get an index within the colors array
    color_index = hash_value % len(colors)
    
    return colors[color_index]

@register.filter
def avatar_color_class(username):
    """Generate a CSS class name for avatar background color based on username."""
    # Create a hash of the username
    hash_object = hashlib.md5(username.encode())
    hash_value = int(hash_object.hexdigest(), 16)
    
    # Use modulo to get a class index (1-10)
    color_index = (hash_value % 10) + 1
    
    return f"avatar-bg-{color_index}" 