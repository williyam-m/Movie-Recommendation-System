# Generated by Django 5.0.4 on 2024-05-19 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_review_movie_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='no_of_likes',
            field=models.IntegerField(default=0),
        ),
    ]
