"""
gargoyle.templatetags.gargoyle_helpers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

from django import template

register = template.Library()


@register.filter
def render_field(field, value=None):
    return field.render(value)


@register.filter
def sort_by_key(field, currently):
    is_negative = currently.find('-') is 0
    current_field = currently.lstrip('-')

    if current_field == field and is_negative:
        return field
    elif current_field == field:
        return '-' + field
    else:
        return field


@register.filter
def sort_field(sort_string):
    return sort_string.lstrip('-')
