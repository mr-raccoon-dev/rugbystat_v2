# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-04 09:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='name',
            field=models.CharField(default='N/A', max_length=127, verbose_name='Базовое название'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stadium',
            name='name',
            field=models.CharField(default='N/A', max_length=127, verbose_name='Базовое название'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tagobject',
            name='story',
            field=models.TextField(blank=True, verbose_name='История'),
        ),
    ]
