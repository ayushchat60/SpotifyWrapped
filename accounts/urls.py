# accounts/urls.py
from django.urls import path
from .views import RegisterView, LoginView, SpotifyAuthView, SpotifyCallbackView, FetchSpotifyWrappedView, SpotifyAuthURLView, ProtectedView, SpotifyLinkCheckView, SpotifyWrappedDataView, UserProfileView, WrappedHistoryView, get_user_tracks, delete_account
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path("protected/", ProtectedView.as_view(), name="protected_view"),
    path('spotify/auth/', SpotifyAuthView.as_view(), name='spotify-auth'),
    path("spotify/callback/", SpotifyCallbackView.as_view(), name="spotify-callback"),
    path('spotify/wrapped-data/<str:term>/', SpotifyWrappedDataView.as_view(), name='spotify-wrapped-data'),
    path('spotify/wrapped-data/<str:term>/<int:id>/', FetchSpotifyWrappedView.as_view(), name="spotify-wrapped-data"),
    path('spotify/auth-url/', SpotifyAuthURLView.as_view(), name='spotify-auth-url'),
    path("spotify/link-check/", SpotifyLinkCheckView.as_view(), name="spotify-link-check"),
    path("spotify/wrapped-history/", WrappedHistoryView.as_view(), name="wrapped-history"),
    path('spotify/user-tracks/<str:term>/', get_user_tracks, name='user-tracks'),
    path('users/delete/', delete_account, name='delete_account'),
]