# Generated by Django 4.2.7 on 2023-11-29 05:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_sendbirdticket'),
    ]

    operations = [
        migrations.AddField(
            model_name='sendbirdticket',
            name='channel_url',
            field=models.URLField(null=True),
        ),
    ]
