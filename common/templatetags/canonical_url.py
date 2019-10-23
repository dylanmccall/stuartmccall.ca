from django.template import Library
from django.utils.six import string_types

from collections import Iterable
from pprint import pprint
import itertools

register = Library()

"""
Template debug tools borrowed from https://github.com/calebsmith/django-template-debug.
"""

@register.simple_tag(takes_context=True)
def canonical_url(context, location=None):
    request = context['request']
    return request.build_absolute_uri(location)
