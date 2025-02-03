import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import Genre, Person, Movie

# Check if the genre already exists
action, created = Genre.objects.get_or_create(name="Action", slug="action")

# Check if the person already exists
chris, created = Person.objects.get_or_create(name="Christopher Nolan", role="director", slug="chris-nolan")

# Create a new movie
movie, created = Movie.objects.get_or_create(
    title="Inception",
    slug="inception",
    release_date="2010-07-16",
    duration=148,
    defaults={"description": "A mind-bending thriller", "poster": "path/to/poster.jpg"}
)

# Add the director to the movie
if created:
    movie.directors.add(chris)
    movie.genres.add(action)