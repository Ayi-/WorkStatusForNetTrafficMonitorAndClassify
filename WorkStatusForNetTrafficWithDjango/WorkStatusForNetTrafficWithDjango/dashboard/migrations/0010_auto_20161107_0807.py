# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-07 08:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0009_auto_20161107_0146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='urldata',
            name='title',
            field=models.CharField(blank=True, max_length=2047),
        ),
        migrations.AlterField(
            model_name='urldata',
            name='title_key',
            field=models.CharField(blank=True, max_length=2047),
        ),
    ]