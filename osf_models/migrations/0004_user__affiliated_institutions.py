# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-05-03 23:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('osf_models', '0003_auto_20160503_1826'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='_affiliated_institutions',
            field=models.ManyToManyField(to='osf_models.Node'),
        ),
    ]
