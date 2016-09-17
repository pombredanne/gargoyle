"""
gargoyle
~~~~~~~~

:copyright: (c) 2010 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""
from django.utils.module_loading import autodiscover_modules

from gargoyle.manager import gargoyle

__version__ = '1.2.6'
VERSION = __version__  # old version compat

__all__ = ('gargoyle', 'autodiscover', '__version__', 'VERSION')

default_app_config = 'gargoyle.apps.GargoyleAppConfig'


def autodiscover():
    """
    Auto-discover INSTALLED_APPS' gargoyle modules and fail silently when
    not present. This forces an import on them to register any gargoyle bits they
    may want.
    """
    import gargoyle.builtins  # noqa
    autodiscover_modules('gargoyle')
