from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from social_django.models import UserSocialAuth
from .models import Movie, UserProfile, Community
from .forms import UserRegistrationForm, ForumThreadForm, ReviewForm
from django.views import View
from django.db.models import Q
from django.conf import settings
from django.core.cache import cache
import requests


def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "en-US",
        "append_to_response": "credits,videos"  # Fetch credits (cast/crew) and videos (trailers)
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None


def fetch_movies():
    # Check if movies are already cached
    cached_movies = cache.get("trending_movies")
    if cached_movies:
        return cached_movies

    # Fetch movies from TMDB API if not cached
    url = "https://api.themoviedb.org/3/trending/movie/week"
    params = {
        "api_key": settings.TMDB_API_KEY,  # Use the API key from settings.py
        "language": "en-US",
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        movies = response.json().get("results", [])
        # Cache the movies for 1 hour (3600 seconds)
        cache.set("trending_movies", movies, timeout=3600)
        return movies
    else:
        # Handle API errors (e.g., return an empty list or log the error)
        return []



def homepage(request):
    movies = fetch_movies()
    context = {"movies": movies,
        'testimonials': UserProfile.objects.all()
    }
    return render(request, 'myapp/home.html', context)

def movie_detail_view(request, movie_id):
    movie = fetch_movie_details(movie_id)
    if not movie:
        return render(request, "404.html", status=404)
    
    context = {
        "movie": movie,
        "cast": movie.get("credits", {}).get("cast", [])[:10],  # Top 10 cast members
        "trailers": [video for video in movie.get("videos", {}).get("results", []) if video["site"] == "YouTube"],
    }
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.movie_id = movie_id
            review.save()
            return redirect('movie_detail', movie_id=movie_id)
    else:
        form = ReviewForm()
    
    context['form'] = form
    return render(request, 'myapp/movie_detail.html', context)

@login_required
def user_profile_view(request, user_id):
    user_profile, created = UserProfile.objects.get_or_create(user_id=user_id)
    context = {'user': user_profile}
    return render(request, 'myapp/user_profile.html', context)

def community_view(request):
    community = Community.objects.first()
    if request.method == 'POST':
        form = ForumThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.user = request.user
            thread.save()
            community.forum_threads.add(thread)
            return redirect('community')
    else:
        form = ForumThreadForm()
    context = {
        'forum_threads': community.forum_threads.all(),
        'gamification_elements': community.gamification_elements.all(),
        'sponsored_content': community.sponsored_content.all(),
        'form': form
    }
    return render(request, 'myapp/community.html', context)


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('homepage')
    else:
        form = AuthenticationForm()
    return render(request, 'myapp/login.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('homepage')
    else:
        form = UserRegistrationForm()
    return render(request, 'myapp/signup.html', {'form': form})

# movies/views.py
class WatchlistToggleView(LoginRequiredMixin, View):
    def post(self, request, slug):
        movie = get_object_or_404(Movie, slug=slug)
        user = request.user
        if user.watchlist.filter(slug=movie.slug).exists():
            user.watchlist.remove(movie)
        else:
            user.watchlist.add(movie)
        return JsonResponse({"status": "success", "action": "added" if movie not in user.watchlist else "removed"})
    
# def get_queryset(self):
#     query = self.request.GET.get("q")
#     return Movie.objects.filter(
#         Q(title__icontains=query) |
#         Q(genres__name__icontains(query)) |
#         Q(directors__name__icontains(query)) |
#         Q(cast__name__icontains(query))
#     ).distinct().prefetch_related('genres', 'directors', 'cast')