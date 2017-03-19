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
def set_trace(context):
    try:
        import ipdb as pdb
    except ImportError:
        import pdb
        print("For best results, pip install ipdb.")
    print("Variables that are available in the current context:")
    render = lambda s: template.Template(s).render(context)
    availables = _get_variables(context)
    pprint(availables)
    print('Type `availables` to show this list.')
    print('Type <variable_name> to access one.')
    print('Use render("template string") to test template rendering')
    # Cram context variables into the local scope
    for var in availables:
        locals()[var] = context[var]
    pdb.set_trace()
    return ''


def _get_variables(context):
    """
    Given a context, return a sorted list of variable names in the context
    """
    return sorted(set(_flatten(context.dicts)))


def _flatten(iterable):
    """
    Given an iterable with nested iterables, generate a flat iterable
    """
    for i in iterable:
        if isinstance(i, Iterable) and not isinstance(i, string_types):
            for sub_i in _flatten(i):
                yield sub_i
        else:
            yield i
