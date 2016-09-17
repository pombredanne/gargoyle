# -*- encoding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from django.core.management import call_command


def test_no_migrations_required(db):
    try:
        call_command('makemigrations', 'gargoyle', exit=1)
    except SystemExit:
        pass
    else:
        assert False, "Migrations required"
