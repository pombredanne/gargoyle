from __future__ import absolute_import, division, print_function, unicode_literals

from django.test import TestCase

from gargoyle import gargoyle
from gargoyle.manager import SwitchManager
from gargoyle.models import DISABLED, GLOBAL, Switch
from gargoyle.testutils import switches


class SwitchContextManagerTest(TestCase):
    def setUp(self):
        self.gargoyle = SwitchManager(Switch, key='key', value='value', instances=True, auto_create=True)

    def test_as_decorator(self):
        switch = self.gargoyle['test']
        switch.status = DISABLED

        @switches(self.gargoyle, test=True)
        def test():
            return self.gargoyle.is_active('test')

        assert test()
        assert self.gargoyle['test'].status == DISABLED

        switch.status = GLOBAL
        switch.save()

        @switches(self.gargoyle, test=False)
        def test2():
            return self.gargoyle.is_active('test')

        assert not test2()
        assert self.gargoyle['test'].status == GLOBAL

    def test_context_manager(self):
        switch = self.gargoyle['test']
        switch.status = DISABLED

        with switches(self.gargoyle, test=True):
            assert self.gargoyle.is_active('test')

        assert self.gargoyle['test'].status == DISABLED

        switch.status = GLOBAL
        switch.save()

        with switches(self.gargoyle, test=False):
            assert not self.gargoyle.is_active('test')

        assert self.gargoyle['test'].status == GLOBAL


@switches(my_switch_name=True)
class SwitchContextManagerClassTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super(SwitchContextManagerClassTest, cls).setUpClass()
        cls.suc_switch_value = gargoyle['my_switch_name']

    def setUp(self):
        super(SwitchContextManagerClassTest, self).setUp()
        self.su_switch_value = gargoyle['my_switch_name']

    def test_it_applied_at_all_levels(self):
        assert self.suc_switch_value
        assert self.su_switch_value
        assert gargoyle['my_switch_name']
