from django.urls import path
from .views import ArtistProfileView, AlbumView, MusicView

urlpatterns = [
    path('profile/', ArtistProfileView.as_view(), name='artist-profile'),
    path('albums/', AlbumView.as_view(), name='artist-albums'),
    path('tracks/', MusicView.as_view(), name='artist-tracks'),
]