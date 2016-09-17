# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gargoyle', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='switch',
            name='status',
            field=models.PositiveSmallIntegerField(
                default=1,
                choices=[(1, 'Disabled'), (2, 'Selective'), (3, 'Global'), (4, 'Inherit')],
            ),
        ),
    ]
