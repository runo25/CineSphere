from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    profile_pic = models.ImageField(upload_to="profiles/", blank=True)
    bio = models.TextField(blank=True)
    watchlist = models.ManyToManyField("Movie", blank=True)
    preferred_genres = models.ManyToManyField("Genre", blank=True)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='myapp_user_groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='myapp_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

class Person(models.Model):
    ROLES = [("actor", "Actor"), ("director", "Director")]
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLES)
    filmography = models.ManyToManyField("Movie", blank=True)
    slug = models.SlugField(unique=True)

class Movie(models.Model):
    directors = models.ManyToManyField(Person, related_name="directed_movies", limit_choices_to={'role': 'director'})
    cast = models.ManyToManyField(Person, related_name="acted_movies", limit_choices_to={'role': 'actor'})
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    release_date = models.DateField()
    duration = models.PositiveIntegerField()  # Minutes
    poster = models.ImageField(upload_to="posters/")
    genres = models.ManyToManyField(Genre)
    average_rating = models.FloatField(default=0.0)

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class TopTenList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    movies = models.ManyToManyField(Movie)

class Badge(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="badges/")
    description = models.TextField()

class ForumThread(models.Model):
    title = models.CharField(max_length=200)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()

class GamificationElement(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="gamification_elements/")
    description = models.TextField()

class SponsoredContent(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="sponsored_content/")
    link = models.URLField()

class Community(models.Model):
    name = models.CharField(max_length=200, unique=True, default="Default Community")  # Ensure names are unique
    forum_threads = models.ManyToManyField(ForumThread, related_name="communities", blank=True)
    gamification_elements = models.ManyToManyField(GamificationElement, blank=True)
    sponsored_content = models.ManyToManyField(SponsoredContent, blank=True)

    def __str__(self):
        return self.name  # Makes the model more readable in the admin panel

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.SET_NULL, null=True, blank=True)
    earnings = models.PositiveIntegerField(default=0)
    top_ten_lists = models.ManyToManyField(TopTenList, blank=True)
    weekly_picks = models.ManyToManyField(Movie, blank=True)
    badges = models.ManyToManyField(Badge, blank=True)
