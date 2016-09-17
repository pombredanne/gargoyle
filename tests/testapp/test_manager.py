from __future__ import absolute_import, division, print_function, unicode_literals

from django.test import TestCase

from gargoyle.manager import SwitchManager
from gargoyle.models import Switch


class ConstantTest(TestCase):
    def setUp(self):
        self.gargoyle = SwitchManager(Switch, key='key', value='value', instances=True)

    def test_disabled(self):
        assert self.gargoyle.DISABLED == 1

    def test_selective(self):
        assert self.gargoyle.SELECTIVE == 2

    def test_global(self):
        assert self.gargoyle.GLOBAL == 3

    def test_include(self):
        assert self.gargoyle.INCLUDE == 'i'

    def test_exclude(self):
        assert self.gargoyle.EXCLUDE == 'e'
