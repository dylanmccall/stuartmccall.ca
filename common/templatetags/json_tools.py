from django.template import Library
from django.utils.functional import Promise

from collections import OrderedDict

import json

register = Library()

@register.filter
def json_dumps(json_object):
    if isinstance(json_object, Promise):
        json_object = OrderedDict(json_object)
    return json.dumps(json_object)

@register.filter
def json_dumps_pretty(json_object):
    if isinstance(json_object, Promise):
        json_object = OrderedDict(json_object)
    return json.dumps(json_object, indent=4, separators=(',', ': '))
