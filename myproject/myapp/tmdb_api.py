# myapp/tmdb_api.py
import requests
from django.conf import settings
from django.core.cache import cache
from django.utils.text import slugify
from .models import Movie, Genre, Person

def fetch_movies():
    # Check if movies are already cached
    cached_movies = cache.get("trending_movies")
    if cached_movies:
        return cached_movies

    # Fetch movies from TMDB API if not cached
    url = "https://api.themoviedb.org/3/trending/movie/week"
    params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "en-US",
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        movies = response.json().get("results", [])
        # Cache the movies for 1 hour (3600 seconds)
        cache.set("trending_movies", movies[:4], timeout=3600)  # Top 4 movies
        return movies[:4]
    else:
        return []
    
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "en-US",
        "append_to_response": "credits"
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        movie_data = response.json()
        
        # Extract basic movie details
        tmdb_id = movie_data.get("id")
        title = movie_data.get("title")
        overview = movie_data.get("overview", "")
        release_date = movie_data.get("release_date")
        duration = movie_data.get("runtime", 0)
        poster_path = movie_data.get("poster_path", "")
        average_rating = movie_data.get("vote_average", 0.0)
        
        # Create or update the movie
        movie, created = Movie.objects.update_or_create(
            tmdb_id=tmdb_id,
            defaults={
                "title": title,
                "slug": slugify(title),
                "description": overview,
                "release_date": release_date,
                "duration": duration,
                "poster": f"https://image.tmdb.org/t/p/original{poster_path}",
                "average_rating": average_rating,
            }
        )
        
        # Save genres
        genres = movie_data.get("genres", [])
        for genre_data in genres:
            genre, _ = Genre.objects.get_or_create(
                tmdb_id=genre_data["id"],
                defaults={"name": genre_data["name"]}
            )
            movie.genres.add(genre)
        
        # Save directors and cast
        credits = movie_data.get("credits", {})
        
        # Save directors
        crew = credits.get("crew", [])
        for crew_member in crew:
            if crew_member["job"] == "Director":
                director, _ = Person.objects.get_or_create(
                    tmdb_id=crew_member["id"],
                    defaults={
                        "name": crew_member["name"],
                        "role": "director",  # Set the role explicitly
                    }
                )
                movie.directors.add(director)
        
        # Save cast
        cast = credits.get("cast", [])
        for cast_member in cast:
            actor, _ = Person.objects.get_or_create(
                tmdb_id=cast_member["id"],
                defaults={
                    "name": cast_member["name"],
                    "role": "actor",  # Set the role explicitly
                }
            )
            movie.cast.add(actor)
        
        return movie
    return None


