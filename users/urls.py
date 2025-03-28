from django.urls import path, include
from .views.auth import SignupView, LoginView, RefreshTokenView
from .views.approval import ApproveUserView, PendingUsersView
from .views.dashboard import UnifiedDashboardView  

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

# Combine all URL patterns
urlpatterns = [
    path('auth/', include(auth_urlpatterns)),
    path('admin/', include(admin_urlpatterns)),
    path('dashboard/', include(dashboard_urlpatterns)),
]