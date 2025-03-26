from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("users.urls")),
    path("api/users/artists/", include("artists.urls")),
    path("api/albums/", include("albums.urls")),  
    path("api/", include("music.urls")),  
]