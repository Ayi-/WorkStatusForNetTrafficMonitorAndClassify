# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-16 12:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_auto_20160916_1110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='localauth',
            name='user_id',
            field=models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, to='dashboard.User', unique=True),
        ),
    ]
