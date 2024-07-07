# Generated by Django 5.0.4 on 2024-04-21 13:15

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movie',
            name='tags',
        ),
        migrations.AddField(
            model_name='admin',
            name='date_time',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AddField(
            model_name='movie',
            name='movie_image',
            field=models.ImageField(default='h', upload_to='movie_images'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='date_time',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
