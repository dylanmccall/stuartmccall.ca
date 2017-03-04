from django.template import Library

import json

register = Library()

@register.filter
def json_dumps(json_object):
    return json.dumps(json_object)

@register.filter
def json_dumps_pretty(json_object):
    return json.dumps(json_object, indent=4, separators=(',', ': '))

@register.filter
def json_data(json_object, path_str):
    path = path_str.split('.')
    while isinstance(json_object, dict) and len(path) > 0:
        part = path.pop(0)
        json_object = json_object.get(part)
    return json_object
