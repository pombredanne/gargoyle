from __future__ import absolute_import, division, print_function, unicode_literals

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory as OrigRequestFactory


class RequestFactory(OrigRequestFactory):

    def request(self, **kwargs):
        user = kwargs.pop('user', AnonymousUser())
        request = super(RequestFactory, self).request(**kwargs)
        request.user = user
        return request
