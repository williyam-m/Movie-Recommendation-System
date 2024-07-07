from django.urls import path
from . import views

urlpatterns = [
    path('movie/view/<str:movieid>', views.movie, name='movie'),
    path('user/dashboard', views.dashboard, name='dashboard'),
    path('', views.home, name='home'),

    path('movie/addmovie', views.addMovie, name='addmovie'),
    path('movie/editmovie/<str:movieid>', views.editMovie, name='editmovie'),
    path('movie/deletemovie/<str:movieid>', views.deleteMovie, name='deletemovie'),
    path('user/search', views.searchMovie, name='searchmovie'),
    path('movie/bookmark/', views.bookmark, name='bookmark'),
    path('movie/like/', views.like, name='like'),
    path('user/mylist', views.myList, name='mylist'),
    path('user/latestmovies', views.latestMovies, name='latestmovies'),

    path('user/signup', views.signup, name='signup'),
    path('user/signin', views.signin, name='signin'),
    path('user/logout', views.logout, name='logout'),
]