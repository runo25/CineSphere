from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('movie/<int:movie_id>/', views.movie_detail_view, name='movie_detail'),
    path('user/<int:user_id>/', views.user_profile_view, name='user_profile'),
    path('community/', views.community_view, name='community'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),  # Add logout URL
]