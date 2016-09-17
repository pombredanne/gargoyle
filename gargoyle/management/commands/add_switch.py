from __future__ import absolute_import, division, print_function, unicode_literals

from django.core.management.base import BaseCommand
from django.utils import six

from gargoyle.models import DISABLED, GLOBAL, Switch


class Command(BaseCommand):
    help = 'Adds or updates the specified gargoyle switch.'

    def add_arguments(self, parser):
        parser.add_argument('switch_name', type=six.text_type)
        parser.add_argument('--disabled', dest='status', action='store_const',
                            default=GLOBAL, const=DISABLED,
                            help='Create a disabled switch.')

    def handle(self, *args, **options):
        switch, created = Switch.objects.get_or_create(
            key=options['switch_name'],
            defaults={
                'status': options['status']
            },
        )
        if not created and switch.status != options['status']:
            switch.status = options['status']
            switch.save()
