from django.urls import path
from .views import  MusicViewSet

urlpatterns = [
    # Music CRUD (within an album context)
    path('albums/<int:album_id>/music/', MusicViewSet.as_view(), name='music-list'),
    path('albums/<int:album_id>/music/<int:music_id>/', MusicViewSet.as_view(), name='music-detail'),
]