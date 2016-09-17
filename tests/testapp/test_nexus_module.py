from __future__ import absolute_import, division, print_function, unicode_literals

import json

from django.contrib.auth.models import User
from django.test import TestCase

from gargoyle import gargoyle
from gargoyle.models import DISABLED, GLOBAL, Switch


class NexusModuleTestCase(TestCase):

    def setUp(self):
        self.user = User(username='user', is_staff=True)
        self.user.set_password('password')
        self.user.save()
        self.client.login(username='user', password='password')

    def test_index(self):
        resp = self.client.get('/nexus/gargoyle/')
        assert resp.status_code == 200
        assert "Gargoyle" in resp.content.decode('utf-8')

    def test_add(self):
        resp = self.client.post('/nexus/gargoyle/add/', {'key': 'key1'})
        assert resp.status_code == 200
        body = json.loads(resp.content.decode('utf-8'))
        assert body['success'] is True
        assert body['data']['key'] == 'key1'
        switch = Switch.objects.get()
        assert switch.key == 'key1'

    def test_update(self):
        Switch.objects.create(key='key1')
        resp = self.client.post('/nexus/gargoyle/update/', {'curkey': 'key1', 'key': 'key2'})
        assert resp.status_code == 200
        body = json.loads(resp.content.decode('utf-8'))
        assert body['success'] is True
        assert body['data']['key'] == 'key2'
        switch = Switch.objects.get()
        assert switch.key == 'key2'

    def test_status(self):
        Switch.objects.create(key='key1', status=DISABLED)
        resp = self.client.post('/nexus/gargoyle/status/', {'key': 'key1', 'status': str(GLOBAL)})
        assert resp.status_code == 200
        body = json.loads(resp.content.decode('utf-8'))
        assert body['success'] is True
        assert body['data']['status'] == GLOBAL
        switch = Switch.objects.get()
        assert switch.status == GLOBAL

    def test_delete(self):
        Switch.objects.create(key='key1')
        resp = self.client.post('/nexus/gargoyle/delete/', {'key': 'key1'})
        assert resp.status_code == 200
        body = json.loads(resp.content.decode('utf-8'))
        assert body['success'] is True
        assert body['data'] == {}
        assert Switch.objects.count() == 0

    def test_add_condition(self):
        switch = Switch.objects.create(key='key1')
        conditions = list(switch.get_active_conditions(gargoyle))
        assert len(conditions) == 0

        resp = self.client.post(
            '/nexus/gargoyle/conditions/add/',
            {'key': 'key1',
             'id': 'gargoyle.builtins.IPAddressConditionSet',
             'field': 'ip_address',
             'ip_address': '1.1.1.1'}
        )
        assert resp.status_code == 200
        body = json.loads(resp.content.decode('utf-8'))
        assert body['success'] is True
        assert body['data']['key'] == 'key1'
        assert len(body['data']['conditions']) == 1

    def test_remove_condition(self):
        switch = Switch.objects.create(key='key1')
        switch.add_condition(gargoyle, 'gargoyle.builtins.IPAddressConditionSet', 'ip_address', '1.1.1.1')
        conditions = list(switch.get_active_conditions(gargoyle))
        assert len(conditions) == 1

        resp = self.client.post(
            '/nexus/gargoyle/conditions/remove/',
            {'key': 'key1',
             'id': 'gargoyle.builtins.IPAddressConditionSet',
             'field': 'ip_address',
             'value': '1.1.1.1'}
        )
        assert resp.status_code == 200
        body = json.loads(resp.content.decode('utf-8'))
        assert body['success'] is True
        assert body['data']['key'] == 'key1'
        assert len(body['data']['conditions']) == 0
