Usage
=====

Gargoyle is designed to work around a very simple API. Generally, you pass in the switch key and a list of instances
to check this key against.

``@switch_is_active``
~~~~~~~~~~~~~~~~~~~~~

The simplest way to use Gargoyle is as a decorator. The decorator will automatically integrate with filters registered
to the ``User`` model, as well as IP address (using ``RequestConditionSet``):

.. code-block:: python

    from gargoyle.decorators import switch_is_active

    @switch_is_active('my switch name')
    def my_view(request):
        return 'foo'

In the case of the switch being inactive and you are using the decorator, a 404 error is raised. You may also redirect
the user to an absolute URL (relative to domain), or a named URL pattern:

.. code-block:: python

    # If redirect_to starts with a /, we assume it's a url path
    @switch_is_active('my switch name', redirect_to='/my/url/path')

    # Alternatively use a name that will be passed to reverse()
    @switch_is_active('my switch name', redirect_to='access_denied')

``gargoyle.is_active``
~~~~~~~~~~~~~~~~~~~~~~

An alternative, more flexible use of Gargoyle is with the ``is_active`` method. This allows you to perform validation
on your own custom objects:

.. code-block:: python

    from gargoyle import gargoyle

    def my_function(request):
        if gargoyle.is_active('my switch name', request):
            return 'foo'
        else:
            return 'bar'

    # with custom objects
    from gargoyle import gargoyle

    def my_method(user):
        if gargoyle.is_active('my switch name', user):
            return 'foo'
        else:
            return 'bar'

Template Tags
~~~~~~~~~~~~~

If you prefer to use templatetags, Gargoyle provides two helpers called ``ifswitch`` and ``ifnotswitch`` to give you
easy conditional blocks based on active switches (for the request):

.. code-block:: django

    {% load gargoyle_tags %}

    {% ifswitch switch_name %}
        switch_name is active!
    {% else %}
        switch_name is not active :(
    {% endifswitch %}

    {% ifnotswitch other_switch_name %}
        other_switch_name is not active!
    {% else %}
        other_switch_name is active!
    {% endifnotswitch %}

The ``else`` clauses are optional.

``ifswitch`` and ``ifnotswitch`` can also be used with custom objects, like the ``gargoyle.is_active`` method:

.. code-block:: django

    {% ifswitch "my switch name" user %}
        "my switch name" is active!
    {% endifswitch %}

Switch Inheritance
~~~~~~~~~~~~~~~~~~

Switches utilizing the named pattern of ``parent:child`` will automatically inherit state from their parents. For
example, if your switch, ``parent:child`` is globally enabled, but ``parent`` is disabled, when
``is_active('parent:child')`` is called it will return ``False``.

A parent switch that has its status set to 'inherit' will return the default value for a switch, which is ``False``
(the same as disabled).

.. note::

    Currently inheritance does not combine filters. If your child defines *any* filters, they will override all of the
    parents.

Testing Switches
~~~~~~~~~~~~~~~~

Gargoyle includes a context manager, which may optionally be used as a decorator, to give temporary state to a switch
on the currently executing thread.

.. code-block:: python

    from gargoyle.testutils import switches

    @switches(my_switch_name=True)
    def test_switches_overrides():
        assert gargoyle.is_active('my_switch_name')  # passes

    def test_switches_context_manager():
        with switches(my_switch_name=True):
            assert gargoyle.is_active('my_switch_name')  # passes

You may also optionally pass an instance of ``SwitchManager`` as the first argument:

.. code-block:: python

    def test_context_manager_alt_gargoyle():
        with switches(gargoyle, my_switch_name=True):
            assert gargoyle.is_active('my_switch_name')  # passes
