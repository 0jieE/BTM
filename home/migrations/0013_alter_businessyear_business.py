# Generated by Django 5.0.7 on 2024-12-28 12:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0012_businessyear'),
    ]

    operations = [
        migrations.AlterField(
            model_name='businessyear',
            name='business',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.business'),
        ),
    ]
