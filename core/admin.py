from django.contrib import admin
from .models import Movie, Bookmark, Like, History

# Register your models here.
admin.site.register(Movie)
admin.site.register(Bookmark)
admin.site.register(Like)
admin.site.register(History)