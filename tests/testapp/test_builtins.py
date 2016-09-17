from __future__ import absolute_import, division, print_function, unicode_literals

import socket

from django.test import RequestFactory, TestCase
from django.test.utils import override_settings

from gargoyle.builtins import HostConditionSet, IPAddressConditionSet
from gargoyle.manager import SwitchManager
from gargoyle.models import SELECTIVE, Switch


class IPAddressConditionSetTests(TestCase):

    condition_set = 'gargoyle.builtins.IPAddressConditionSet'

    def setUp(self):
        super(IPAddressConditionSetTests, self).setUp()
        self.gargoyle = SwitchManager(Switch, key='key', value='value', instances=True, auto_create=True)
        self.gargoyle.register(IPAddressConditionSet())
        self.request_factory = RequestFactory()

        Switch.objects.create(key='test', status=SELECTIVE)
        self.switch = self.gargoyle['test']
        assert not self.gargoyle.is_active('test')

    def test_percent(self):
        self.switch.add_condition(
            condition_set=self.condition_set,
            field_name='percent',
            condition='0-100',
        )

        request = self.request_factory.get('/', REMOTE_ADDR='1.0.0.0')
        assert self.gargoyle.is_active('test', request)

    def test_0_percent(self):
        self.switch.add_condition(
            condition_set=self.condition_set,
            field_name='percent',
            condition='0-0',
        )

        request = self.request_factory.get('/', REMOTE_ADDR='1.0.0.0')
        assert not self.gargoyle.is_active('test', request)

    def test_specific_address(self):
        self.switch.add_condition(
            condition_set=self.condition_set,
            field_name='ip_address',
            condition='1.1.1.1',
        )

        request = self.request_factory.get('/', REMOTE_ADDR='1.0.0.0')
        assert not self.gargoyle.is_active('test', request)

        request = self.request_factory.get('/', REMOTE_ADDR='1.1.1.1')
        assert self.gargoyle.is_active('test', request)

    @override_settings(INTERNAL_IPS=['1.0.0.0'])
    def test_internal_ip(self):
        self.switch.add_condition(
            condition_set=self.condition_set,
            field_name='internal_ip',
            condition='',
        )

        request = self.request_factory.get('/', REMOTE_ADDR='1.0.0.0')
        assert self.gargoyle.is_active('test', request)

        request = self.request_factory.get('/', REMOTE_ADDR='1.1.1.1')
        assert not self.gargoyle.is_active('test', request)

    @override_settings(INTERNAL_IPS=['1.0.0.0'])
    def test_not_internal_ip(self):
        self.switch.add_condition(
            condition_set=self.condition_set,
            field_name='internal_ip',
            condition='',
            exclude=True,
        )

        request = self.request_factory.get('/', REMOTE_ADDR='1.0.0.0')
        assert not self.gargoyle.is_active('test', request)

        request = self.request_factory.get('/', REMOTE_ADDR='1.1.1.1')
        assert self.gargoyle.is_active('test', request)


class HostConditionSetTest(TestCase):
    def setUp(self):
        self.gargoyle = SwitchManager(Switch, key='key', value='value', instances=True, auto_create=True)
        self.gargoyle.register(HostConditionSet())

    def test_simple(self):
        condition_set = 'gargoyle.builtins.HostConditionSet'

        # we need a better API for this (model dict isnt cutting it)
        switch = Switch.objects.create(
            key='test',
            status=SELECTIVE,
        )
        switch = self.gargoyle['test']

        assert not self.gargoyle.is_active('test')

        switch.add_condition(
            condition_set=condition_set,
            field_name='hostname',
            condition=socket.gethostname(),
        )

        assert self.gargoyle.is_active('test')
