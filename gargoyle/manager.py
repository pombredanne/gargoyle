from __future__ import absolute_import, division, print_function, unicode_literals

from django.conf import settings
from django.core.cache import caches
from django.http import HttpRequest
from django.utils import six
from django.utils.functional import SimpleLazyObject
from modeldict import ModelDict

from gargoyle.proxy import SwitchProxy

from .constants import DISABLED, EXCLUDE, GLOBAL, INCLUDE, INHERIT, SELECTIVE


class SwitchManager(ModelDict):
    DISABLED = DISABLED
    SELECTIVE = SELECTIVE
    GLOBAL = GLOBAL
    INHERIT = INHERIT

    INCLUDE = INCLUDE
    EXCLUDE = EXCLUDE

    def __init__(self, *args, **kwargs):
        self._registry = {}
        super(SwitchManager, self).__init__(*args, **kwargs)

    def __repr__(self):
        return "<%s: %s (%s)>" % (self.__class__.__name__, self.model, self._registry.values())

    def __getitem__(self, key):
        """
        Returns a SwitchProxy, rather than a Switch. It allows us to
        easily extend the Switches method and automatically include our
        manager instance.
        """
        return SwitchProxy(self, super(SwitchManager, self).__getitem__(key))

    def is_active(self, key, *instances, **kwargs):
        """
        Returns ``True`` if any of ``instances`` match an active switch. Otherwise
        returns ``False``.

        >>> gargoyle.is_active('my_feature', request)
        """
        default = kwargs.pop('default', False)

        # Check all parents for a disabled state
        parts = key.split(':')
        if len(parts) > 1:
            child_kwargs = kwargs.copy()
            child_kwargs['default'] = None
            result = self.is_active(':'.join(parts[:-1]), *instances, **child_kwargs)

            if result is False:
                return result
            elif result is True:
                default = result

        try:
            switch = self[key]
        except KeyError:
            # switch is not defined, defer to parent
            return default

        if switch.status == GLOBAL:
            return True
        elif switch.status == DISABLED:
            return False
        elif switch.status == INHERIT:
            return default

        conditions = switch.value
        # If no conditions are set, we inherit from parents
        if not conditions:
            return default

        if instances:
            # HACK: support request.user by swapping in User instance
            instances = list(instances)
            for v in instances:
                if isinstance(v, HttpRequest) and hasattr(v, 'user'):
                    instances.append(v.user)

        # check each switch to see if it can execute
        return_value = False

        for switch in six.itervalues(self._registry):
            result = switch.has_active_condition(conditions, instances)
            if result is False:
                return False
            elif result is True:
                return_value = True

        # there were no matching conditions, so it must not be enabled
        return return_value

    def register(self, condition_set):
        """
        Registers a condition set with the manager.

        >>> condition_set = MyConditionSet()
        >>> gargoyle.register(condition_set)
        """

        if callable(condition_set):
            registerable = condition_set()
        else:
            registerable = condition_set
        self._registry[registerable.get_id()] = registerable
        return condition_set

    def unregister(self, condition_set):
        """
        Unregisters a condition set with the manager.

        >>> gargoyle.unregister(condition_set)
        """
        if callable(condition_set):
            registerable = condition_set()
        else:
            registerable = condition_set
        popped = self._registry.pop(registerable.get_id(), None)
        return (popped is not None)

    def get_condition_set_by_id(self, switch_id):
        """
        Given the identifier of a condition set (described in
        ConditionSet.get_id()), returns the registered instance.
        """
        return self._registry[switch_id]

    def get_condition_sets(self):
        """
        Returns a generator yielding all currently registered
        ConditionSet instances.
        """
        return six.itervalues(self._registry)

    def get_all_conditions(self):
        """
        Returns a generator which yields groups of lists of conditions.

        >>> for set_id, label, field in gargoyle.get_all_conditions():
        >>>     print("%(label)s: %(field)s" % (label, field.label))
        """
        for condition_set in sorted(self.get_condition_sets(), key=lambda x: x.get_group_label()):
            group = six.text_type(condition_set.get_group_label())
            for field in six.itervalues(condition_set.fields):
                yield condition_set.get_id(), group, field


def make_gargoyle():
    from gargoyle.models import Switch

    kwargs = {
        'key': 'key',
        'value': 'value',
        'instances': True,
        'auto_create': getattr(settings, 'GARGOYLE_AUTO_CREATE', True),
    }

    if hasattr(settings, 'GARGOYLE_CACHE_NAME'):
        kwargs['cache'] = caches[settings.GARGOYLE_CACHE_NAME]

    return SwitchManager(Switch, **kwargs)

gargoyle = SimpleLazyObject(make_gargoyle)
