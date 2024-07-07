from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime
from datetime import date

User = get_user_model()
# Create your models here.

class Bookmark(models.Model):
    user_id = models.IntegerField()
    movie_id = models.CharField(max_length=100)   # post id is uuid. so, not a number

class History(models.Model):
    user_id = models.IntegerField()
    movie_id = models.CharField(max_length=100)   # post id is uuid. so, not a number

class Like(models.Model):
    user_id = models.IntegerField()
    movie_id = models.CharField(max_length=100)   # post id is uuid. so, not a number


class Movie(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4)
    user = models.CharField(max_length=100)
    movie_image = models.ImageField(upload_to='movie_images')
    movie_video = models.FileField(upload_to='movie_videos')
    title = models.TextField()
    overview = models.TextField()
    genre = models.TextField()
    views = models.IntegerField(default=0)
    no_of_likes = models.IntegerField(default=0)

    def __str__(self):
        return self.user


