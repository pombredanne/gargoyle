"""
:copyright: (c) 2010 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import nexus
from django.conf.urls import include, url
from django.contrib import admin
from django.http import HttpResponse
from django.views.generic.base import RedirectView

from gargoyle.compat import subinclude


admin.autodiscover()
nexus.autodiscover()

urlpatterns = [
    url(r'^nexus/', include(nexus.site.urls)),
    url(r'^admin/', subinclude(admin.site.urls)),
    url(r'^foo/$', lambda request: HttpResponse(), name='gargoyle_test_foo'),
    url(r'^/?$', RedirectView.as_view(url='/nexus/', permanent=False)),
]
