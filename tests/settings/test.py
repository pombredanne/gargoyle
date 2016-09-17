"""
Used for the test suite run.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

from copy import deepcopy

from .base import *  # noqa
from .base import DATABASES, TEMPLATES

DEBUG = False

DATABASES = deepcopy(DATABASES)
del DATABASES['default']['NAME']


TEMPLATES = deepcopy(TEMPLATES)
TEMPLATES[0]['OPTIONS']['debug'] = False
