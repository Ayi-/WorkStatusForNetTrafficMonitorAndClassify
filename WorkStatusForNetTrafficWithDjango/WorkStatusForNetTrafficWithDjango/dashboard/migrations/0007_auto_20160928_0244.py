# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-28 02:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_auto_20160926_1327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_name',
            field=models.CharField(error_messages={'unique': '\u7528\u6237\u540d\u5df2\u5b58\u5728'}, max_length=255, unique=True),
        ),
    ]