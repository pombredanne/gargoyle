from __future__ import absolute_import, division, print_function, unicode_literals

import pytest
from django.core.validators import ValidationError
from django.test import TestCase

from gargoyle.conditions import ConditionSet, Range
from gargoyle.manager import SwitchManager
from gargoyle.models import SELECTIVE, Switch


class RangeTests(TestCase):

    def test_is_active(self):
        condition = Range()
        assert not condition.is_active('1-2', 0)
        assert condition.is_active('1-2', 1)
        assert condition.is_active('1-2', 2)
        assert not condition.is_active('1-2', 3)

    def test_is_active_should_allow_floats(self):
        condition = Range()
        assert not condition.is_active('1-2', 0.0)
        assert not condition.is_active('1-2', 0.9)
        assert condition.is_active('1-2', 1.0)
        assert condition.is_active('1-2', 1.5)
        assert condition.is_active('1-2', 2.0)
        assert not condition.is_active('1-2', 2.1)
        assert not condition.is_active('1-2', 2.01)
        assert not condition.is_active('1-2', 2.001)
        assert not condition.is_active('1-2', 3.0)
        assert not condition.is_active('1-2', 9e9)

    def test_is_active_shouldnt_allow_strings(self):
        condition = Range()
        assert not condition.is_active('1-2', '0')
        assert not condition.is_active('1-2', '1')
        assert not condition.is_active('1-2', '2')
        assert not condition.is_active('1-2', '3')

    def test_clean_success(self):
        condition = Range()
        assert condition.clean('1-2') == '1-2'

    def test_clean_fail_empty(self):
        condition = Range()
        with pytest.raises(ValidationError):
            condition.clean('')

    def test_clean_fail_no_dash(self):
        condition = Range()
        with pytest.raises(ValidationError):
            condition.clean('1')

    def test_clean_fail_no_second_number(self):
        condition = Range()
        with pytest.raises(ValidationError):
            condition.clean('1-')

    def test_clean_fail_no_first_number(self):
        condition = Range()
        with pytest.raises(ValidationError):
            condition.clean('-2')

    def test_clean_fail_no_numbers(self):
        condition = Range()
        with pytest.raises(ValidationError):
            condition.clean('-')

    def test_clean_fail_too_many_numbers(self):
        condition = Range()
        with pytest.raises(ValidationError):
            condition.clean('1-2-3')


class NumberConditionSet(ConditionSet):
    in_range = Range()

    def get_field_value(self, instance, field_name):
        if field_name == 'in_range':
            return instance


class NumberConditionSetTests(TestCase):

    condition_set = __name__ + '.' + NumberConditionSet.__name__

    def setUp(self):
        super(NumberConditionSetTests, self).setUp()
        self.gargoyle = SwitchManager(Switch, key='key', value='value', instances=True, auto_create=True)
        self.gargoyle.register(NumberConditionSet())

        Switch.objects.create(key='test', status=SELECTIVE)
        self.switch = self.gargoyle['test']

    def test_range(self):
        self.switch.add_condition(
            condition_set=self.condition_set,
            field_name='in_range',
            condition='1-3',
        )

        assert not self.gargoyle.is_active('test', 0)
        assert self.gargoyle.is_active('test', 1)
        assert self.gargoyle.is_active('test', 2)
        assert self.gargoyle.is_active('test', 3)
        assert not self.gargoyle.is_active('test', 4)
