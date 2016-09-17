"""
:copyright: (c) 2010 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import datetime

import pytest
from django.contrib.auth.models import AnonymousUser, User
from django.core.cache import cache
from django.http import Http404, HttpResponse
from django.test import TestCase
from django.test.utils import override_settings

from gargoyle.builtins import IPAddressConditionSet, UserConditionSet
from gargoyle.decorators import switch_is_active
from gargoyle.manager import SwitchManager
from gargoyle.models import DISABLED, GLOBAL, INHERIT, SELECTIVE, Switch
from testapp.utils import RequestFactory


class APITest(TestCase):

    request_factory = RequestFactory()

    def setUp(self):
        self.user = User.objects.create(username='foo', email='foo@example.com')
        self.gargoyle = SwitchManager(Switch, key='key', value='value', instances=True, auto_create=True)
        self.gargoyle.register(UserConditionSet(User))
        self.gargoyle.register(IPAddressConditionSet())

    def test_register_unregister_class(self):
        klass = IPAddressConditionSet
        registered = self.gargoyle.register(IPAddressConditionSet)
        assert registered is klass

        unregistered = self.gargoyle.unregister(klass)
        assert unregistered

        unregistered = self.gargoyle.unregister(klass)
        assert not unregistered

    def test_register_unregister_instance(self):
        condition_set = IPAddressConditionSet()
        registered = self.gargoyle.register(condition_set)
        assert registered is condition_set

        unregistered = self.gargoyle.unregister(condition_set)
        assert unregistered

        unregistered = self.gargoyle.unregister(condition_set)
        assert not unregistered

    def test_builtin_registration(self):
        assert 'gargoyle.builtins.UserConditionSet(auth.user)' in self.gargoyle._registry
        assert 'gargoyle.builtins.IPAddressConditionSet' in self.gargoyle._registry
        assert len(list(self.gargoyle.get_condition_sets())) == 2

    def test_user(self):
        condition_set = 'gargoyle.builtins.UserConditionSet(auth.user)'

        switch = Switch.objects.create(key='test', status=SELECTIVE)
        switch = self.gargoyle['test']

        switch.add_condition(
            condition_set=condition_set,
            field_name='percent',
            condition='0-50',
        )

        user = User(pk=5)
        assert self.gargoyle.is_active('test', user)

        user = User(pk=8771)
        assert not self.gargoyle.is_active('test', user)

        switch.add_condition(
            condition_set=condition_set,
            field_name='is_staff',
            condition='1',
        )

        user = User(pk=8771, is_staff=True)
        assert self.gargoyle.is_active('test', user)

        user = User(pk=8771, is_superuser=True)
        assert not self.gargoyle.is_active('test', user)

        switch.add_condition(
            condition_set=condition_set,
            field_name='is_superuser',
            condition='1',
        )

        user = User(pk=8771, is_superuser=True)
        assert self.gargoyle.is_active('test', user)

        # test with request
        request = self.request_factory.get('/', user=user)
        assert self.gargoyle.is_active('test', request)

        # test date joined condition
        user = User(pk=8771)
        assert not self.gargoyle.is_active('test', user)

        switch.add_condition(
            condition_set=condition_set,
            field_name='date_joined',
            condition='2011-07-01',
        )

        user = User(pk=8771, date_joined=datetime.datetime(2011, 7, 2))
        assert self.gargoyle.is_active('test', user)

        user = User(pk=8771, date_joined=datetime.datetime(2012, 7, 2))
        assert self.gargoyle.is_active('test', user)

        user = User(pk=8771, date_joined=datetime.datetime(2011, 6, 2))
        assert not self.gargoyle.is_active('test', user)

        user = User(pk=8771, date_joined=datetime.datetime(2011, 7, 1))
        assert self.gargoyle.is_active('test', user)

        switch.clear_conditions(condition_set=condition_set)
        switch.add_condition(
            condition_set=condition_set,
            field_name='email',
            condition='bob@example.com',
        )

        user = User(pk=8771, email="bob@example.com")
        assert self.gargoyle.is_active('test', user)

        user = User(pk=8771, email="bob2@example.com")
        assert not self.gargoyle.is_active('test', user)

        user = User(pk=8771)
        assert not self.gargoyle.is_active('test', user)

    def test_exclusions(self):
        condition_set = 'gargoyle.builtins.UserConditionSet(auth.user)'

        switch = Switch.objects.create(key='test', status=SELECTIVE)
        switch = self.gargoyle['test']

        switch.add_condition(
            condition_set=condition_set,
            field_name='is_staff',
            condition='1',
        )
        switch.add_condition(
            condition_set=condition_set,
            field_name='username',
            condition='foo',
        )
        switch.add_condition(
            condition_set=condition_set,
            field_name='username',
            condition='bar',
            exclude=True
        )

        user = User(pk=0, username='foo', is_staff=False)
        assert self.gargoyle.is_active('test', user)

        user = User(pk=0, username='foo', is_staff=True)
        assert self.gargoyle.is_active('test', user)

        user = User(pk=0, username='bar', is_staff=False)
        assert not self.gargoyle.is_active('test', user)

        user = User(pk=0, username='bar', is_staff=True)
        assert not self.gargoyle.is_active('test', user)

    def test_only_exclusions(self):
        condition_set = 'gargoyle.builtins.UserConditionSet(auth.user)'

        switch = Switch.objects.create(key='test', status=SELECTIVE)
        switch = self.gargoyle['test']

        # Intent is that this condition is True for all users *except* if the
        # username == bar
        switch.add_condition(
            condition_set=condition_set,
            field_name='username',
            condition='bar',
            exclude=True
        )

        # username=='foo', so should be active
        user = User(pk=0, username='foo', is_staff=False)
        assert self.gargoyle.is_active('test', user)

        # username=='foo', so should be active
        user = User(pk=0, username='foo', is_staff=True)
        assert self.gargoyle.is_active('test', user)

        # username=='bar', so should not be active
        user = User(pk=0, username='bar', is_staff=False)
        assert not self.gargoyle.is_active('test', user)

        # username=='bar', so should not be active
        user = User(pk=0, username='bar', is_staff=True)
        assert not self.gargoyle.is_active('test', user)

    def test_decorator_for_user(self):
        condition_set = 'gargoyle.builtins.UserConditionSet(auth.user)'

        switch = Switch.objects.create(key='test', status=DISABLED)
        switch = self.gargoyle['test']

        @switch_is_active('test')
        def test(request):
            return True

        request = self.request_factory.get('/', user=self.user)

        with pytest.raises(Http404):
            test(request)

        switch.status = SELECTIVE
        switch.save()

        with pytest.raises(Http404):
            test(request)

        switch.add_condition(
            condition_set=condition_set,
            field_name='username',
            condition='foo',
        )

        assert test(request)

    def test_decorator_for_ip_address(self):
        condition_set = 'gargoyle.builtins.IPAddressConditionSet'

        switch = Switch.objects.create(key='test', status=DISABLED)
        switch = self.gargoyle['test']

        @switch_is_active('test')
        def test(request):
            return True

        request = self.request_factory.get('/', REMOTE_ADDR='192.168.1.1')

        with pytest.raises(Http404):
            test(request)

        switch.status = SELECTIVE
        switch.save()

        switch.add_condition(
            condition_set=condition_set,
            field_name='ip_address',
            condition='192.168.1.1',
        )

        assert test(request)

        # add in a second condition, so that removing the first one won't kick
        # in the "no conditions returns is_active True for selective switches"
        switch.add_condition(
            condition_set=condition_set,
            field_name='ip_address',
            condition='192.168.1.2',
        )

        switch.remove_condition(
            condition_set=condition_set,
            field_name='ip_address',
            condition='192.168.1.1',
        )

        with pytest.raises(Http404):
            test(request)

        switch.add_condition(
            condition_set=condition_set,
            field_name='ip_address',
            condition='192.168.1.1',
        )

        assert test(request)

        switch.clear_conditions(
            condition_set=condition_set,
            field_name='ip_address',
        )

        switch.add_condition(
            condition_set=condition_set,
            field_name='percent',
            condition='50-100',
        )

        assert test(request)

        switch.clear_conditions(
            condition_set=condition_set,
        )

        switch.add_condition(
            condition_set=condition_set,
            field_name='percent',
            condition='0-50',
        )

        with pytest.raises(Http404):
            test(request)

    def test_decorator_with_redirect(self):
        Switch.objects.create(key='test', status=DISABLED)

        request = self.request_factory.get('/', user=self.user)

        @switch_is_active('test', redirect_to='/foo')
        def test(request):
            return HttpResponse()

        response = test(request)
        assert response.status_code, 302
        assert 'Location' in response
        assert response['Location'] == '/foo'

        @switch_is_active('test', redirect_to='gargoyle_test_foo')
        def test2(request):
            return HttpResponse()

        response = test2(request)
        assert response.status_code, 302
        assert 'Location' in response
        assert response['Location'] == '/foo/'

    def test_global(self):
        switch = Switch.objects.create(key='test', status=DISABLED)
        switch = self.gargoyle['test']

        assert not self.gargoyle.is_active('test')
        assert not self.gargoyle.is_active('test', self.user)

        switch.status = GLOBAL
        switch.save()

        assert self.gargoyle.is_active('test')
        assert self.gargoyle.is_active('test', self.user)

    def test_disable(self):
        switch = Switch.objects.create(key='test')

        switch = self.gargoyle['test']

        switch.status = DISABLED
        switch.save()

        assert not self.gargoyle.is_active('test')

        assert not self.gargoyle.is_active('test', self.user)

    def test_deletion(self):
        switch = Switch.objects.create(key='test')

        switch = self.gargoyle['test']

        assert 'test' in self.gargoyle

        switch.delete()

        assert 'test' not in self.gargoyle

    def test_expiration(self):
        switch = Switch.objects.create(key='test')

        switch = self.gargoyle['test']

        switch.status = DISABLED
        switch.save()

        assert not self.gargoyle.is_active('test')

        Switch.objects.filter(key='test').update(value={}, status=GLOBAL)

        # cache shouldn't have expired
        assert not self.gargoyle.is_active('test')

        cache_key = self.gargoyle.remote_cache_key
        # in memory cache shouldnt have expired
        cache.delete(cache_key)
        assert not self.gargoyle.is_active('test')
        switch.status, switch.value = GLOBAL, {}
        # Ensure post save gets sent
        self.gargoyle._post_save(sender=None, instance=switch, created=False)

        # any request should expire the in memory cache
        self.client.get('/')

        assert self.gargoyle.is_active('test')

    def test_anonymous_user(self):
        condition_set = 'gargoyle.builtins.UserConditionSet(auth.user)'

        switch = Switch.objects.create(key='test')

        switch = self.gargoyle['test']

        switch.status = SELECTIVE
        switch.save()

        user = AnonymousUser()

        assert not self.gargoyle.is_active('test', user)

        switch.add_condition(
            condition_set=condition_set,
            field_name='percent',
            condition='1-10',
        )

        assert not self.gargoyle.is_active('test', user)

        switch.clear_conditions(condition_set=condition_set)

        assert not self.gargoyle.is_active('test', user)

        switch.add_condition(
            condition_set=condition_set,
            field_name='is_anonymous',
            condition='1',
        )

        assert self.gargoyle.is_active('test', user)

        switch.add_condition(
            condition_set=condition_set,
            field_name='percent',
            condition='1-10',
        )

        assert self.gargoyle.is_active('test', user)

    def test_ip_address_internal_ips(self):
        condition_set = 'gargoyle.builtins.IPAddressConditionSet'

        Switch.objects.create(key='test', status=SELECTIVE)
        switch = self.gargoyle['test']

        request = self.request_factory.get('/', REMOTE_ADDR='192.168.1.1')

        assert not self.gargoyle.is_active('test', request)

        switch.add_condition(
            condition_set=condition_set,
            field_name='internal_ip',
            condition='1',
        )

        with override_settings(INTERNAL_IPS=['192.168.1.1']):
            assert self.gargoyle.is_active('test', request)

        assert not self.gargoyle.is_active('test', request)

    def test_ip_address(self):
        condition_set = 'gargoyle.builtins.IPAddressConditionSet'

        switch = Switch.objects.create(key='test', status=SELECTIVE)
        switch = self.gargoyle['test']

        request = self.request_factory.get('/', REMOTE_ADDR='192.168.1.1')

        assert not self.gargoyle.is_active('test', request)

        switch.add_condition(
            condition_set=condition_set,
            field_name='ip_address',
            condition='192.168.1.1',
        )

        assert self.gargoyle.is_active('test', request)

        switch.clear_conditions(condition_set=condition_set)
        switch.add_condition(
            condition_set=condition_set,
            field_name='ip_address',
            condition='127.0.0.1',
        )

        assert not self.gargoyle.is_active('test', request)

        switch.clear_conditions(condition_set=condition_set)

        assert not self.gargoyle.is_active('test', request)

        switch.add_condition(
            condition_set=condition_set,
            field_name='percent',
            condition='50-100',
        )

        assert self.gargoyle.is_active('test', request)

        assert self.gargoyle.is_active('test', self.request_factory.get('/', REMOTE_ADDR='192.168.1.1'))

        switch.clear_conditions(condition_set=condition_set)
        switch.add_condition(
            condition_set=condition_set,
            field_name='percent',
            condition='0-50',
        )
        assert not self.gargoyle.is_active('test', request)

        assert self.gargoyle.is_active('test', self.request_factory.get('/', REMOTE_ADDR='::1'))

        switch.clear_conditions(condition_set=condition_set)
        switch.add_condition(
            condition_set=condition_set,
            field_name='percent',
            condition='0-50',
        )
        assert not self.gargoyle.is_active('test', request)

    def test_to_dict(self):
        condition_set = 'gargoyle.builtins.IPAddressConditionSet'

        switch = Switch.objects.create(
            label='my switch',
            description='foo bar baz',
            key='test',
            status=SELECTIVE,
        )

        switch.add_condition(
            manager=self.gargoyle,
            condition_set=condition_set,
            field_name='ip_address',
            condition='192.168.1.1',
        )

        result = switch.to_dict(self.gargoyle)

        assert result['label'] == 'my switch'
        assert result['status'] == SELECTIVE
        assert result['description'] == 'foo bar baz'
        assert result['key'] == 'test'
        assert len(result['conditions']) == 1

        condition = result['conditions'][0]
        assert condition['id'] == condition_set
        assert condition['label'] == 'IP Address'
        assert len(condition['conditions']) == 1

        inner_condition = condition['conditions'][0]
        assert len(inner_condition) == 4
        assert inner_condition[0] == 'ip_address'
        assert inner_condition[1] == '192.168.1.1'
        assert inner_condition[2] == '192.168.1.1'
        assert not inner_condition[3]

    def test_remove_condition(self):
        condition_set = 'gargoyle.builtins.UserConditionSet(auth.user)'

        switch = Switch.objects.create(
            key='test',
            status=SELECTIVE,
        )
        switch = self.gargoyle['test']

        user5 = User(pk=5, email='5@example.com')

        # inactive if selective with no conditions
        assert not self.gargoyle.is_active('test', user5)

        user8771 = User(pk=8771, email='8771@example.com', is_superuser=True)
        switch.add_condition(
            condition_set=condition_set,
            field_name='is_superuser',
            condition='1',
        )
        assert self.gargoyle.is_active('test', user8771)
        # No longer is_active for user5 as we have other conditions
        assert not self.gargoyle.is_active('test', user5)

        switch.remove_condition(
            condition_set=condition_set,
            field_name='is_superuser',
            condition='1',
        )

        # back to inactive for everyone with no conditions
        assert not self.gargoyle.is_active('test', user5)
        assert not self.gargoyle.is_active('test', user8771)

    def test_add_condition_empty(self):
        condition_set = 'gargoyle.builtins.UserConditionSet(auth.user)'

        switch = Switch.objects.create(key='test', status=SELECTIVE)
        switch = self.gargoyle['test']

        user_empty = User(email='')
        user_non_empty = User(email='test@example.com')
        switch.add_condition(
            condition_set=condition_set,
            field_name='email',
            condition='',
        )

        assert self.gargoyle.is_active('test', user_empty)
        assert not self.gargoyle.is_active('test', user_non_empty)

    def test_switch_defaults(self):
        """Test that defaults pulled from GARGOYLE_SWITCH_DEFAULTS.

        Requires SwitchManager to use auto_create.

        """
        assert self.gargoyle.is_active('active_by_default')
        assert not self.gargoyle.is_active('inactive_by_default')

        assert self.gargoyle['inactive_by_default'].label == 'Default Inactive'
        assert self.gargoyle['active_by_default'].label == 'Default Active'

        active_by_default = self.gargoyle['active_by_default']
        active_by_default.status = DISABLED
        active_by_default.save()
        assert not self.gargoyle.is_active('active_by_default')

    def test_invalid_condition(self):
        condition_set = 'gargoyle.builtins.UserConditionSet(auth.user)'

        switch = Switch.objects.create(
            key='test',
            status=SELECTIVE,
        )
        switch = self.gargoyle['test']

        user5 = User(pk=5, email='5@example.com')

        # inactive if selective with no conditions
        assert not self.gargoyle.is_active('test', user5)

        user8771 = User(pk=8771, email='8771@example.com', is_superuser=True)
        switch.add_condition(
            condition_set=condition_set,
            field_name='foo',
            condition='1',
        )
        assert not self.gargoyle.is_active('test', user8771)

    def test_inheritance(self):
        condition_set = 'gargoyle.builtins.UserConditionSet(auth.user)'

        # we need a better API for this (model dict isnt cutting it)
        switch = Switch.objects.create(key='test', status=SELECTIVE)
        switch = self.gargoyle['test']

        switch.add_condition(
            condition_set=condition_set,
            field_name='percent',
            condition='0-50',
        )

        switch = Switch.objects.create(key='test:child', status=INHERIT)
        switch = self.gargoyle['test']

        user = User(pk=5)
        assert self.gargoyle.is_active('test:child', user)

        user = User(pk=8771)
        assert not self.gargoyle.is_active('test:child', user)

        switch = self.gargoyle['test']
        switch.status = DISABLED

        user = User(pk=5)
        assert not self.gargoyle.is_active('test:child', user)

        user = User(pk=8771)
        assert not self.gargoyle.is_active('test:child', user)

        switch = self.gargoyle['test']
        switch.status = GLOBAL

        user = User(pk=5)
        assert self.gargoyle.is_active('test:child', user)

        user = User(pk=8771)
        assert self.gargoyle.is_active('test:child', user)

    def test_parent_override_child_state(self):
        Switch.objects.create(key='test', status=DISABLED)

        Switch.objects.create(key='test:child', status=GLOBAL)

        assert not self.gargoyle.is_active('test:child')

    def test_child_state_is_used(self):
        Switch.objects.create(key='test', status=GLOBAL)

        Switch.objects.create(key='test:child', status=DISABLED)

        assert not self.gargoyle.is_active('test:child')

    def test_parent_override_child_condition(self):
        condition_set = 'gargoyle.builtins.UserConditionSet(auth.user)'

        Switch.objects.create(key='test', status=SELECTIVE)

        parent = self.gargoyle['test']

        parent.add_condition(
            condition_set=condition_set,
            field_name='username',
            condition='bob',
        )

        Switch.objects.create(key='test:child', status=GLOBAL)

        user = User(username='bob')
        assert self.gargoyle.is_active('test:child', user)

        user = User(username='joe')
        assert not self.gargoyle.is_active('test:child', user)

        assert not self.gargoyle.is_active('test:child')

    def test_child_condition_differing_than_parent_loses(self):
        condition_set = 'gargoyle.builtins.UserConditionSet(auth.user)'

        Switch.objects.create(key='test', status=SELECTIVE)

        parent = self.gargoyle['test']

        parent.add_condition(
            condition_set=condition_set,
            field_name='username',
            condition='bob',
        )

        Switch.objects.create(key='test:child', status=SELECTIVE)

        child = self.gargoyle['test:child']

        child.add_condition(
            condition_set=condition_set,
            field_name='username',
            condition='joe',
        )

        user = User(username='bob')
        assert not self.gargoyle.is_active('test:child', user)

        user = User(username='joe')
        assert not self.gargoyle.is_active('test:child', user)

        user = User(username='john')
        assert not self.gargoyle.is_active('test:child', user)

        assert not self.gargoyle.is_active('test:child')

    def test_child_condition_including_parent_wins(self):
        condition_set = 'gargoyle.builtins.UserConditionSet(auth.user)'

        Switch.objects.create(key='test', status=SELECTIVE)

        parent = self.gargoyle['test']

        parent.add_condition(
            condition_set=condition_set,
            field_name='username',
            condition='bob',
        )

        Switch.objects.create(key='test:child', status=SELECTIVE)

        child = self.gargoyle['test:child']

        child.add_condition(
            condition_set=condition_set,
            field_name='username',
            condition='bob',
        )
        child.add_condition(
            condition_set=condition_set,
            field_name='username',
            condition='joe',
        )

        user = User(username='bob')
        assert self.gargoyle.is_active('test:child', user)

        user = User(username='joe')
        assert not self.gargoyle.is_active('test:child', user)

        user = User(username='john')
        assert not self.gargoyle.is_active('test:child', user)

        assert not self.gargoyle.is_active('test:child')
