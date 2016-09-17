"""
Exists to ensure you can always log in with admin/password when running in
'dev' mode - see tests/README.rst
"""
from __future__ import absolute_import, division, print_function, unicode_literals

from django.contrib.auth.models import User
from django.contrib.staticfiles.management.commands.runserver import Command as BaseCommand
from django.core.management import call_command

from gargoyle.models import SELECTIVE, Switch


class Command(BaseCommand):
    def check_migrations(self):
        call_command('migrate', interactive=True)

        if not User.objects.exists():
            self.stdout.write(
                "Welcome to Gargoyle test mode\n"
                "Login with username 'admin', password 'password'"
            )
            user = User(username='admin', is_superuser=True, is_staff=True)
            user.set_password('password')
            user.save()

        if not Switch.objects.exists():
            Switch.objects.create(
                label="Example Switch",
                key='example_switch',
                description="This is an example switch prebuilt for trying out the nexus interface",
                status=SELECTIVE,
            )
