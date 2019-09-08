# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-09-08 10:47
from __future__ import unicode_literals

from django.db import migrations, models


def update_matches(apps, schema_editor):
    Match = apps.get_model('matches', 'Match')
    for match in Match.objects.all():
        match.display_name = match.name
        date = ""
        if match.date:
            date = match.date.strftime("%Y-%m-%d")
        match.name = "{} {}".format(date, match.display_name)
        match.save()

class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0013_match_date_unknown'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='display_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Отображение'),
        ),
        migrations.RunPython(update_matches, migrations.RunPython.noop),
    ]
