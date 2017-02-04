# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-15 07:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0019_titleclassificationlib_title_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='titleclassificationlib',
            name='title',
            field=models.CharField(blank=True, default=b'', max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='titleclassificationlib',
            name='title_key',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='urldata',
            name='title',
            field=models.CharField(blank=True, default=b'', max_length=255),
        ),
    ]
