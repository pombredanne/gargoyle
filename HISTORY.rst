.. :changelog:

=======
History
=======

Pending Release
---------------

* New release notes here

1.2.6 (2016-08-03)
------------------

* Set requirements to exclude ``django-jsonfield==1.0.0`` which is broken for
  PostgreSQL - use ``1.0.1+`` instead.
* Made ``gargoyle.register()`` usable as a decorator
* Made ``gargoyle.unregister()`` return the boolean value of whether something
  was unregistered.
* Fixed removing conditions where the value is the empty string.

1.2.5 (2016-05-09)
------------------

* Removed debug prints from ``conditions.py`` which spammed your WSGI logs.

1.2.4 (2016-05-02)
------------------

* Added a migration to tidy up ``bytes`` versus ``str`` for ``choices`` on
  ``Switch.status``. It's no-op as ``choices`` is in-memory only.

1.2.3 (2016-04-11)
------------------

* Bugfix for ``@switches`` which didn't work on ``TestCase`` classes properly
  in 1.2.2.

1.2.2 (2016-04-11)
------------------

* Removed the South Migrations, since South doesn't support Django 1.7+, and
  Gargoyle only supports Django 1.8+.
* Added all ``__future__`` imports to all files for Python 2.7/3
  compatibility.
* Made ``@switches`` usable as a class decorator for ``unittest.TestCase``
  classes as well, where it applies from ``setUpClass`` through all tests to
  ``tearDownClass``. This adds a dependency on ``contextdecorator`` on Python
  2.7.

1.2.1 (2016-02-25)
------------------

* Simplified autodiscovery code to use ``AppConfig.ready()``. It's no longer
  necessary to add a call to ``gargoyle.autodiscover()`` in your ``urls.py``,
  when not using Nexus.
* Fixed url ``patterns`` warnings that appear on Django 1.9

1.2.0 (2016-02-12)
------------------

* Fixed the splitting of ``Range`` conditions, a merge of disqus/gargoyle#55,
  thanks @matclayton.
* Fixed the parsing of ``Range`` conditions for the Nexus admin interface.
* Fixed the Nexus interface to work with Switches that contain dots in their
  names, a merge of disqus/gargoyle#73, thanks @Raekkeri.
* Removed all inline javascript.
* Added ``ifnotswitch`` template tag, a merge of disqus/gargoyle#92, thanks
  @mrfuxi.
* Fixed Nexus admin interface for Switches with spaces in their keys, an issue
  reported in disqus/gargoyle#98, thanks @arnaudlimbourg.

1.1.1 (2016-01-15)
------------------

* Fix jQuery Templates

1.1.0 (2016-01-14)
------------------

*This version has a broken UI, please upgrade*

* Support for Django 1.9
* Use the YPlan fork of ``django-modeldict``
* Removed support for Django 1.7
* Added support for Python 3.4 and 3.5

1.0.1 (2015-12-09)
------------------

* Fix requirements to use ``nexus-yplan`` not ``nexus``

1.0.0 (2015-12-09)
------------------

* Forked by YPlan
* Django 1.8 compatibility - use Django migrations

0.11.0 (2015-02-03)
-------------------

* Better support for Django 1.6 and Django 1.7
* Dropped support for Django 1.2 and Django 1.3
* Use ``model_name`` in favour of ``module_name`` if available (deprecation in Django 1.6)
* DateTimeFields now utilize the auto_now=True kwarg
* Travis now tests on Django 1.6/Django 1.7

0.7.3 (2012-01-31)
------------------

* Bump ModelDict version to handle expiration in Celery tasks.

0.7.2 (2012-01-31)
------------------

* Correct issue with trying to serialize datetime objects.

0.7.1 (2012-01-31)
------------------

* Changed the behavior of gargoyle.testutils.switches to monkey patch
  the is_active method which should solve scenarios where switches
  are reloaded during the context.

0.7.0 (2012-01-27)
------------------

* Added confirmation message for enabling switches globally.
* Added date modified and sorts for switches on index view.

0.6.1 (2011-12-19)
------------------

* Require Nexus >= 0.2.0

0.6.0 (2011-12-16)
------------------

* Added basic switch inheritance.
* Added auto collapsing of switch details in interface.
* Added simple search filtering of switches in interface.

0.5.2 (2011-12-06)
------------------

* Improved display of Gargoyle dashboard widget.

0.5.1 (2011-12-06)
------------------

* Fixed switch_condition_removed signal to pass ``switch`` instance.

0.5.0 (2011-12-06)
------------------

* Updated signals to pass more useful information in each one (including the switch).

0.4.0
-----

* The percent field is now available on all ModelConditionSet's by default.
* Fixed a CSRF conflict issue with Nexus.

0.3.0 (2011-08-15)
------------------

- Added gargoyle.testutils.with_switches decorator
- Added gargoyle.testutils.SwitchContextManager

0.2.4
-----

- Updated autodiscovery code to resemble Django's newer example
- Updated django-modeldict to 1.1.6 to solve a threading issue with registration
- Added GARGOYLE_AUTO_CREATE setting to disable auto creation of new switches
- Added the ability to pass arbitrary objects to the ifswitch template tag.

0.2.3 (2011-07-12)
------------------

- Ensure HostConditionSet is registered

0.2.2 (2011-07-06)
------------------

- Moved tests outside of gargoyle namespace

0.2.1
-----

- UI tweaks

0.2.0
-----

- [Backwards Incompatible] SELECTIVE switches without conditions are now inactive
- Added ConditionSet.has_active_condition, and support for default NoneType instances
  for global / environment checks.
- Added HostConditionSet which allows you to specify a switch for a single
  server hostname
