# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-14 13:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0012_auto_20161114_1319'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='urldata',
            name='kinds',
        ),
        migrations.AddField(
            model_name='titlecut',
            name='category',
            field=models.CharField(blank=True, default=b'', max_length=50),
        ),
    ]