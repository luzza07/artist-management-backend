from django.urls import path, include
from .views.auth import SignupView, LoginView, RefreshTokenView
from .views.approval import ApproveUserView, PendingUsersView
from .views.dashboard import UnifiedDashboardView  
from .views.management import *

# Authentication URLs
auth_urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh-token/', RefreshTokenView.as_view(), name='refresh-token'),
]

# Admin URLs
admin_urlpatterns = [
    path('approve-user/', ApproveUserView.as_view(), name='approve-user'),
    path('pending-users/', PendingUsersView.as_view(), name='pending-users'),
]

# Dashboard URLs
dashboard_urlpatterns = [
    path('', UnifiedDashboardView.as_view(), name='unified_dashboard'),
]

management_urlpatterns = [
    # User management (for super_admin)
    path('admin/users/create/', CreateUserView.as_view(), name='create_user'),  # super_admin can create user
    path('admin/users/', ListUsersView.as_view(), name='list_users'),  # super_admin can list users
    path('admin/users/<int:user_id>/update/', UpdateUserView.as_view(), name='update_user'),  # super_admin can update user
    path('admin/users/<int:user_id>/delete/', DeleteUserView.as_view(), name='delete_user'),  # super_admin can delete user

    # Artist management (for super_admin and artist_manager)
    path('admin/artists/create/', CreateArtistView.as_view(), name='create_artist'),  # super_admin can create artist
    path('admin/artists/', ListArtistsView.as_view(), name='list_artists'),  # super_admin can list artists
    path('admin/artists/<int:artist_id>/update/', UpdateArtistView.as_view(), name='update_artist'),  # super_admin can update artist
    path('admin/artists/<int:artist_id>/delete/', DeleteArtistView.as_view(), name='delete_artist'),  # super_admin can delete artist

    # Artist manager management (only for artist_manager)
    path('artist-manager/artists/create/', CreateArtistView.as_view(), name='create_artist_manager'),  # artist_manager can create artist
    path('artist-manager/artists/', ListArtistsView.as_view(), name='list_artists_manager'),  # artist_manager can list artists
    path('artist-manager/artists/<int:artist_id>/update/', UpdateArtistView.as_view(), name='update_artist_manager'),  # artist_manager can update artist
    path('artist-manager/artists/<int:artist_id>/delete/', DeleteArtistView.as_view(), name='delete_artist_manager'),  # artist_manager can delete artist
]

# Combine all URL patterns
urlpatterns = [
    path('auth/', include(auth_urlpatterns)),
    path('admin/', include(admin_urlpatterns)),
    path('dashboard/', include(dashboard_urlpatterns)),
    path('management/',include(management_urlpatterns)),
]