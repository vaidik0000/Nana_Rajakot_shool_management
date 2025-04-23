from django import template

register = template.Library()

@register.filter
def get(dictionary, key):
    """
    Gets a value from a dictionary using the given key.
    Usage: {{ dictionary|get:key }}
    """
    return dictionary.get(key, None)

@register.filter
def get_dict_value(dictionary, key):
    """Safely get a value from a dictionary using a key."""
    if dictionary and key in dictionary:
        return dictionary[key]
    return None

@register.filter
def get_nested_value(dictionary, keys):
    """Safely get a value from a nested dictionary using a dot-separated key path."""
    if not dictionary:
        return None
    
    current = dictionary
    for key in keys.split('.'):
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    return current

@register.filter
def get_timetable_entry(timetable_dict, params):
    """
    Get a timetable entry from a nested dictionary structure.
    Usage: {{ timetable_dict|get_timetable_entry:"class:day:period" }}
    """
    if not timetable_dict:
        return None
    
    parts = params.split(':')
    if len(parts) != 3:
        return None
    
    class_id, day_id, period_id = parts
    
    try:
        if class_id in timetable_dict and day_id in timetable_dict[class_id] and period_id in timetable_dict[class_id][day_id]:
            return timetable_dict[class_id][day_id][period_id]
    except (KeyError, TypeError):
        pass
    
    return None 