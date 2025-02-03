from django.contrib import admin
from .models import User, Genre, Person, Movie, Review, TopTenList, Badge, ForumThread, GamificationElement, SponsoredContent, UserProfile, Community

admin.site.register(User)
admin.site.register(Genre)
admin.site.register(Person)
admin.site.register(Movie)
admin.site.register(Review)
admin.site.register(TopTenList)
admin.site.register(Badge)
admin.site.register(ForumThread)
admin.site.register(GamificationElement)
admin.site.register(SponsoredContent)
admin.site.register(UserProfile)
admin.site.register(Community)

# Register your models here.
