from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.index, name='index'),

    # Spotify OAuth
    path('spotify/login/', views.spotify_login, name='spotify_login'),
    path('spotify/callback/', views.spotify_callback, name='spotify_callback'),
    path('spotify/logout/', views.spotify_logout, name='spotify_logout'),

    # Spotify data
    path('spotify/profile/', views.spotify_profile, name='spotify_profile'),
    path('spotify/search/', views.spotify_search, name='spotify_search'),
    path('album/<int:album_id>/', views.album_detail, name='album_detail'),
    path('spotify/top-tracks/', views.spotify_top_tracks, name='spotify_top_tracks'),
    path('spotify/recommendations/', views.spotify_recommendations, name='spotify_recommendations'),
    path('spotify/new-releases/', views.spotify_new_releases, name='spotify_new_releases'),
]
