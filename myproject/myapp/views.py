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

def homepage(request):
    context = {
        'movies': Movie.objects.all(),
        'categories': Movie.objects.values('genres__name').distinct(),
        'testimonials': UserProfile.objects.all()
    }
    return render(request, 'myapp/home.html', context)

def movie_detail_view(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.movie = movie
            review.save()
            return redirect('movie_detail', movie_id=movie.id)
    else:
        form = ReviewForm()
    context = {'movie': movie, 'form': form}
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
    
def get_queryset(self):
    query = self.request.GET.get("q")
    return Movie.objects.filter(
        Q(title__icontains=query) |
        Q(genres__name__icontains=query) |
        Q(directors__name__icontains=query) |
        Q(cast__name__icontains=query)
    ).distinct().prefetch_related('genres', 'directors', 'cast')