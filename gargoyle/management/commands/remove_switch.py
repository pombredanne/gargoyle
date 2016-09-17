from __future__ import absolute_import, division, print_function, unicode_literals

from django.core.management.base import BaseCommand
from django.utils import six

from gargoyle.models import Switch


class Command(BaseCommand):
    help = 'Removes the specified gargoyle switch.'

    def add_arguments(self, parser):
        parser.add_argument('switch_name', type=six.text_type)

    def handle(self, *args, **options):
        Switch.objects.filter(key=options['switch_name']).delete()
