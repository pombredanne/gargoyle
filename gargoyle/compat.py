from __future__ import absolute_import, division, print_function, unicode_literals

import django

# Python 3.2+ includes ContextDecorator, otherwise use backport
try:
    from contextlib import ContextDecorator
except ImportError:
    from contextdecorator import ContextDecorator

# Django 1.9

# url(prefix, include(urls, namespace, name)) -> url(prefix, (urls, namespace, name))
if django.VERSION[:2] >= (1, 9):
    def subinclude(urls_tuple):
        return urls_tuple  # (urls, namespace, name)
else:
    from django.conf.urls import include as subinclude


__all__ = ['ContextDecorator', 'subinclude']
