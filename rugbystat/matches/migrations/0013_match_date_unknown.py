# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-09-08 10:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0012_auto_20190825_1215'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='date_unknown',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='Дата, если неизвестна'),
        ),
    ]
