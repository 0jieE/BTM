# Generated by Django 5.0.7 on 2024-12-29 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0017_picture_business_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='picture',
            name='username',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
