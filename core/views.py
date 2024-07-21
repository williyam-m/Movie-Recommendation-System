from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Movie, Bookmark, Like, History
from django.conf import settings as conf_settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from itertools import chain
from django.db.models import Q
import numpy as np
import pandas as pd
import os
import re
import uuid

# Create your views here.

@login_required(login_url = 'signin')
def dashboard(request):
    user = User.objects.get(username = request.user.username)

    movie_list = Movie.objects.filter(user = user.username)

    return render(request, 'dashboard.html',
                  {'movie_list': movie_list})

@login_required(login_url = 'signin')
def searchMovie(request):
    if request.method == 'POST':
        title = request.POST['title']
        search_results = Movie.objects.filter(title__icontains = title)
        movie_list = []
        for movie in search_results:
            movie_object = Movie.objects.get(id = movie.id)
            movie_list.append(movie_object)

        paginator = Paginator(movie_list, 10)  # Show 10 movies per page

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'movielist.html', {'page_obj': page_obj})

def get_movie_recommendations(all_movies, liked_movies, suggestion_count=10):
    # Create a DataFrame to hold movie data
    movies_data = {
        'id': [str(movie.id) for movie in all_movies],
        'title': [movie.title for movie in all_movies],
        'overview': [movie.overview for movie in all_movies],
        'genre': [movie.genre for movie in all_movies]
    }

    df_movies = pd.DataFrame(movies_data)

    # Combine the title, overview, and genre to create a single feature
    df_movies['features'] = df_movies['title'] + " " + df_movies['overview'] + " " + df_movies['genre']

    # Vectorize the features
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(df_movies['features'])

    # Create a combined feature vector for liked movies
    liked_movie_indices = [df_movies[df_movies['id'] == str(movie.id)].index[0] for movie in liked_movies]
    liked_movie_matrix = tfidf_matrix[liked_movie_indices]
    liked_movie_vector = liked_movie_matrix.mean(axis=0)

    # Convert to numpy array
    liked_movie_vector = np.asarray(liked_movie_vector)

    # Calculate cosine similarity between liked movie vector and all movie vectors
    cosine_sim = cosine_similarity(liked_movie_vector, tfidf_matrix).flatten()

    # Get the indices of the top suggested movies
    similar_indices = cosine_sim.argsort()[-suggestion_count:][::-1]

    # Get the movie IDs of the top suggested movies
    recommended_movie_ids = df_movies.iloc[similar_indices]['id'].tolist()

    return recommended_movie_ids

@login_required(login_url='signin')
def home(request):
    user = request.user

    historys = History.objects.filter(user_id=user.id)
    bookmarks = Bookmark.objects.filter(user_id=user.id)
    likes = Like.objects.filter(user_id=user.id)

    all_movies = Movie.objects.all()
    user_interested_movies = []

    for like in likes:
        user_interested_movies.append(Movie.objects.get(id=like.movie_id))
    for history in historys:
        user_interested_movies.append(Movie.objects.get(id=history.movie_id))
    for bookmark in bookmarks:
        user_interested_movies.append(Movie.objects.get(id=bookmark.movie_id))

    recommended_movies = None
    print(len(user_interested_movies))

    if len(user_interested_movies) > 1:
        recommended_movie_ids = get_movie_recommendations(all_movies, user_interested_movies, suggestion_count=min(len(user_interested_movies) - 1, 10))

        # Fetch the recommended movie objects
        recommended_movies = Movie.objects.filter(id__in=recommended_movie_ids)

    last_seen_movie = None
    if historys.exists():
        last_seen = historys.latest('id')
        last_seen_movie = Movie.objects.get(id=last_seen.movie_id)

    return render(request, 'home.html', {
        'user': user,
        'movie_list': all_movies,
        'recommended_movies': recommended_movies,
        'last_seen_movie': last_seen_movie,
    })

@login_required(login_url='userSignin')
def myList(request):
    bookmarks = Bookmark.objects.filter(user_id=request.user.id)
    bookmarks_movie_list = []
    for bookmark in bookmarks:
        movie_object = Movie.objects.get(id=bookmark.movie_id)
        bookmarks_movie_list.append(movie_object)

    likes = Like.objects.filter(user_id=request.user.id)
    likes_movie_list = []
    for like in likes:
        movie_object = Movie.objects.get(id=like.movie_id)
        likes_movie_list.append(movie_object)

    historys = History.objects.filter(user_id=request.user.id)
    history_movie_list = []
    for history in historys:
        movie_object = Movie.objects.get(id=history.movie_id)
        history_movie_list.append(movie_object)
    return render(request, 'mylist.html',
                  {'bookmarks_movie_list': bookmarks_movie_list,
                   'history_movie_list': history_movie_list,
                   'likes_movie_list': likes_movie_list})



@login_required(login_url='userSignin')
def latestMovies(request):
    movies = Movie.objects.all().order_by('-id')  # Assuming newest movies have higher IDs
    paginator = Paginator(movies, 10)  # Show 10 movies per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'movielist.html', {'page_obj': page_obj})


@login_required(login_url='signin')
def movie(request, movieid):
    movie = Movie.objects.get(id = movieid)
    user = User.objects.get(username= movie.user)

    like = False
    bookmark = False

    #views count
    if user.username != movie.user:
        movie.views = movie.views + 1
        movie.save()

    if  History.objects.filter(user_id=request.user.id, movie_id=movieid).first():
        History.objects.filter(user_id=request.user.id, movie_id=movieid).delete()

    history = History.objects.create(user_id=request.user.id, movie_id=movieid)
    history.save()

    if Bookmark.objects.filter(user_id=request.user.id, movie_id=movieid).first():
        bookmark = True
    else:
        bookmark = False
    if Like.objects.filter(user_id=request.user.id, movie_id=movieid).first():
        like = True
    else:
        like = False

    return render(request, 'movie.html',
                  {'bookmark':bookmark,
                   'like' : like,
                   'movie': movie})


@login_required(login_url='signin')
def addMovie(request):
    if request.method == 'POST':
        movie_image_flag = False
        movie_video_flag = False
        movie_image = None
        user = request.user.username

        title = request.POST['title']
        overview = request.POST['overview']
        genre = request.POST['genre']

        if request.FILES.get('movie_image') != None:
            movie_image = request.FILES.get('movie_image')
            movie_image_flag = True

        if request.FILES.get('movie_video') != None:
            movie_video = request.FILES.get('movie_video')
            movie_video_flag = True

        if len(overview) == 0 or len(genre) == 0 or len(title) == 0:
            messages.info(request, 'Please enter all field')
            return redirect('/movie/addwork')

        else:
            new_movie = Movie.objects.create(user=user, overview=overview, genre=genre, title=title)
            if movie_image_flag:
                new_movie.movie_image = movie_image

            if movie_video_flag:
                new_movie.movie_video = movie_video
            new_movie.save()
            return redirect('/user/dashboard')

    return render(request, 'addmovie.html')


@login_required(login_url='signin')
def deleteMovie(request, movieid):
    movie = Movie.objects.get(id=movieid)

    if (movie.user != request.user.username):
        return redirect('/')
    if movie.movie_image:
        if len(movie.movie_image) > 0:
            os.remove(movie.movie_image.path)
    if movie.movie_video:
        if len(movie.movie_video) > 0:
            os.remove(movie.movie_video.path)

    History.objects.filter(movie_id=movieid).delete()
    Bookmark.objects.filter(movie_id=movieid).delete()
    Like.objects.filter(movie_id=movieid).delete()

    movie.delete()
    return redirect('/user/dashboard')


@login_required(login_url='signin')
def editMovie(request, movieid):
    movie = Movie.objects.get(id=movieid)

    if (movie.user != request.user.username):
        return redirect('/')
    if request.method == 'POST':
        title = request.POST['title']
        overview = request.POST['overview']
        genre = request.POST['genre']

        if len(overview) == 0 or len(genre) == 0 or len(title) == 0:
            messages.info(request, 'Please enter all field')
            return redirect('/movie/editmovie')

        else:
            movie = Movie.objects.get(id = movieid)
            movie.overview=overview
            movie.genre=genre
            movie.title=title

            movie.save()
            return redirect('/user/dashboard')

    return render(request, 'editmovie.html',{"movie":movie})


@login_required(login_url = 'signin')
def bookmark(request):
    if request.method == 'POST':
        movieid = request.POST['movieid']
        if request.user.first_name != "":
            if Bookmark.objects.filter(user_id = request.user.id, movie_id = movieid).first():
                bookmark_object = Bookmark.objects.get(user_id = request.user.id, movie_id = movieid)
                bookmark_object.delete()
                return redirect('/movie/view/' + movieid)
            else:
                bookmark_object = Bookmark.objects.create(user_id = request.user.id, movie_id = movieid)
                bookmark_object.save()
                return redirect('/movie/view/' + movieid)
        return redirect('/movie/view/' + movieid)
    return redirect('/')

@login_required(login_url = 'userSignin')
def like(request):
    if request.method == 'POST':
        movieid = request.POST['movieid']
        if Like.objects.filter(user_id=request.user.id, movie_id=movieid).first():
            like_object = Like.objects.get(user_id=request.user.id, movie_id=movieid)
            like_object.delete()

            movie = Movie.objects.get(id=movieid)
            movie.no_of_likes = movie.no_of_likes - 1
            movie.save()

        else:
            like_object = Like.objects.create(user_id=request.user.id, movie_id=movieid)
            like_object.save()

            movie = Movie.objects.get(id=movieid)
            movie.no_of_likes = movie.no_of_likes + 1
            movie.save()

        return redirect('/movie/view/' + movieid)
    return redirect('/')


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        username_pattern = re.compile(r'^[a-zA-Z0-9._-]+$')
        if not username_pattern.match(username):
            messages.info(request, 'Invalid username!')
            return redirect('/user/signup')

        email_pattern = re.compile(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$')
        if not email_pattern.match(email):
            messages.info(request, 'Invalid email address!')
            return redirect('/user/signup')

        if password == confirm_password:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('/user/signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('/user/signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                # log user in and redirect to settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                return redirect('/user/dashboard')
        else:
            messages.info(request, 'Password Not Matching')
            return redirect('/user/signup')

    else:
        return render(request, 'signup.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/user/dashboard')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('/user/signin')

    else:
        return render(request, 'signin.html')


@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('/user/signin')