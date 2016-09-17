"""
gargoyle.testutils
~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import inspect
import sys
import unittest

from gargoyle import gargoyle
from .compat import ContextDecorator


class TestCaseContextDecorator(ContextDecorator):
    """
    ContextDecorator subclass that allows the sane decoration of TestCase classes by wrapping
    from setUpClass to tearDownClass
    """
    def __call__(self, decorable):
        if inspect.isclass(decorable):
            if not issubclass(decorable, unittest.TestCase):
                raise ValueError("Only supports the wrapping of unittest.TestCase classes")

            klass = decorable

            orig_setUpClass = klass.setUpClass
            orig_tearDownClass = klass.tearDownClass

            def setUpClass(cls):
                self.__enter__()
                try:
                    if orig_setUpClass is not None:
                        super  # Fool SuperCheckPlugin
                        orig_setUpClass()
                except Exception:
                    self.__exit__(*sys.exc_info())
                    raise

            if orig_setUpClass is klass.__dict__.get('setUpClass', None):
                # was defined on this class, state we wrap it
                setUpClass.__wrapped__ = orig_setUpClass

            def tearDownClass(cls):
                if orig_tearDownClass is not None:
                    super  # Fool SuperCheckPlugin
                    orig_tearDownClass()
                self.__exit__(None, None, None)

            if orig_tearDownClass is klass.__dict__.get('tearDownClass', None):
                # was defined on this class, state we wrap it
                tearDownClass.__wrapped__ = orig_tearDownClass

            klass.setUpClass = classmethod(setUpClass)
            klass.tearDownClass = classmethod(tearDownClass)

            return klass
        else:
            decorated = super(TestCaseContextDecorator, self).__call__(decorable)
            if inspect.isfunction(decorable):
                decorated.__wrapped__ = decorable
            return decorated


class SwitchContextManager(TestCaseContextDecorator):
    """
    Allows temporarily enabling or disabling a switch.

    Ideal for testing.

    >>> @switches(my_switch_name=True)
    >>> def foo():
    >>>     print(gargoyle.is_active('my_switch_name'))

    >>> def foo():
    >>>     with switches(my_switch_name=True):
    >>>         print(gargoyle.is_active('my_switch_name'))

    You may also optionally pass an instance of ``SwitchManager``
    as the first argument.

    >>> def foo():
    >>>     with switches(gargoyle, my_switch_name=True):
    >>>         print(gargoyle.is_active('my_switch_name'))

    Can also wrap unittest classes, which includes Django's
    TestCase classes:

    >>> @switches(my_switch_name=True)
    ... class MyTests(TestCase):
    ...     @classmethod
    ...     def setUpTestData(cls):
    ...         # my_switch_name is True here
    ...
    ...     def test_foo(self):
    ...          # ... and here
    """
    def __init__(self, gargoyle=gargoyle, **keys):
        self.gargoyle = gargoyle
        self.is_active_func = gargoyle.is_active
        self.keys = keys
        self._state = {}
        self._values = {
            True: gargoyle.GLOBAL,
            False: gargoyle.DISABLED,
        }

    def __enter__(self):
        self.patch()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unpatch()

    def patch(self):
        def is_active(gargoyle):
            is_active_func = gargoyle.is_active

            def wrapped(key, *args, **kwargs):
                if key in self.keys:
                    return self.keys[key]
                return is_active_func(key, *args, **kwargs)
            return wrapped

        self.gargoyle.is_active = is_active(self.gargoyle)

    def unpatch(self):
        self.gargoyle.is_active = self.is_active_func

switches = SwitchContextManager
