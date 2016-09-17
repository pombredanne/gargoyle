=====
Tests
=====

This directory is a Django project, with ``testapp`` is an example app that
contains the tests and support code.

You can run the tests by running ``tox`` in the root of the repo.

You can also run Django locally to check changes in the browser with a simple
SQLite database with:

.. code-block:: bash

    ./manage.py runserver

This automatically adds the username 'admin' with password 'password' so you
can login locally at ``/admin/`` and peruse Nexus with the Gargoyle interface
at ``/nexus/``.
