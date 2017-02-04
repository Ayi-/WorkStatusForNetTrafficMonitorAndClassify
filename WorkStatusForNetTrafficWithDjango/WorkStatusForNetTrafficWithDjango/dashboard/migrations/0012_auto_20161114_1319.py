# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-14 13:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0011_auto_20161107_0821'),
    ]

    operations = [
        migrations.CreateModel(
            name='TitleCut',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('url_id', models.IntegerField()),
                ('title_key', models.CharField(blank=True, default=b'', max_length=2047)),
            ],
        ),
        migrations.RemoveField(
            model_name='urldata',
            name='title_key',
        ),
    ]
