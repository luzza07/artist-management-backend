from django.urls import path, include
from .views import (
    SignupView, 
    LoginView, 
    ApproveUserView, 
    PendingUsersView,
    RefreshTokenView
)

auth_urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh-token/', RefreshTokenView.as_view(), name='refresh-token'),
]

admin_urlpatterns = [
    path('approve-user/', ApproveUserView.as_view(), name='approve-user'),
    path('pending-users/', PendingUsersView.as_view(), name='pending-users'),
]

urlpatterns = [
    path('auth/', include(auth_urlpatterns)),
    path('admin/', include(admin_urlpatterns)),
]