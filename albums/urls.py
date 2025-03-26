from django.urls import path
from .views import AlbumViewSet

urlpatterns = [
    path('', AlbumViewSet.as_view(), name='album-list'),
    path('<int:album_id>/', AlbumViewSet.as_view(), name='album-detail'),
]