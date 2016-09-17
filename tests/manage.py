#!/usr/bin/env python
"""
Used for running this install of gargoyle locally
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys

MODULE_DIR = os.path.dirname(__file__)

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.dev")
    sys.path.insert(0, os.path.abspath(os.path.join(MODULE_DIR, '..')))

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
