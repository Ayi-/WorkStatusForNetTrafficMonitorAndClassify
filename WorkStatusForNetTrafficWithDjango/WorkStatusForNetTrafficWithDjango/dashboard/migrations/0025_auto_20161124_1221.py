# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-24 12:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0024_auto_20161124_1214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='titleclassificationlib',
            name='title',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]