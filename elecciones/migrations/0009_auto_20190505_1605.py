# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-05 19:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('elecciones', '0008_lugarvotacion_estado_geolocalizacion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mesa',
            name='circuito',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='elecciones.Circuito'),
        ),
    ]
