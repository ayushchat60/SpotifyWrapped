"""
views.py - Handles API endpoints for user authentication, Spotify integration, and
fetching user-specific Spotify Wrapped data.
"""

import logging
import os
from datetime import timedelta
from urllib.parse import urlencode

import requests
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.utils.timezone import now
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Artist, SpotifyToken, Track, WrappedHistory
from .serializers import RegisterSerializer

# Load environment variables
load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')


class RegisterView(APIView):
    """
    API endpoint for user registration.

    Accepts a POST request with user data, validates it, and registers a new user.

    Methods:
        post(request): Handles user registration.
    """
    def post(self, request):  # pylint: disable=unused-argument
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    API endpoint for user login.

    Accepts a POST request with username and password, authenticates the user,
    and returns JWT tokens if successful.

    Methods:
        post(request): Handles user login.
    """
    def post(self, request):  # pylint: disable=unused-argument
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            })
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class UserProfileView(APIView):
    """
    API endpoint to retrieve user profile details.

    Returns the authenticated user's username, email, and Spotify link status.

    Methods:
        get(request): Retrieves user profile information.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):  # pylint: disable=unused-argument
        user = request.user
        return Response({
            "username": user.username,
            "email": user.email,
            "spotify_linked": hasattr(user, "spotifytoken"),  # Check if Spotify is linked
        })


class SpotifyAuthView(APIView):
    """
    API endpoint to provide the Spotify authorization URL.

    Returns a URL to start the Spotify authentication process.

    Methods:
        get(request): Generates and returns the Spotify authorization URL.
    """
    def get(self, request):  # pylint: disable=unused-argument
        url = (
            f"https://accounts.spotify.com/authorize"
            f"?response_type=code&client_id={SPOTIFY_CLIENT_ID}"
            f"&redirect_uri={SPOTIFY_REDIRECT_URI}"
            f"&scope=user-top-read"
        )
        return Response({"url": url}, status=status.HTTP_200_OK)


class ProtectedView(APIView):
    """
    API endpoint to test authentication.

    Returns a message confirming the user is authenticated.

    Methods:
        get(request): Confirms user authentication.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):  # pylint: disable=unused-argument
        return Response({"message": "You are authenticated!"})


class SpotifyCallbackView(APIView):
    """
    API endpoint to handle Spotify OAuth callback.

    Exchanges the authorization code for Spotify access and refresh tokens.

    Methods:
        post(request): Handles the callback and token exchange.
    """
    def post(self, request):  # pylint: disable=unused-argument
        # Handle Spotify callback logic here.
        pass


class FetchSpotifyWrappedView(APIView):
    """
    API endpoint to fetch Spotify Wrapped data.

    Retrieves the user's top artists and tracks for the specified time range.

    Methods:
        get(request, term): Fetches Spotify Wrapped data.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, term):  # pylint: disable=unused-argument
        # Fetch Spotify Wrapped data logic here.
        pass


class SpotifyWrappedDataView(APIView):
    """
    API endpoint to fetch and store user's Spotify Wrapped data.

    Methods:
        get(request, term): Retrieves Wrapped data for the specified term.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, term):  # pylint: disable=unused-argument
        # Fetch and store Spotify Wrapped data logic here.
        pass


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):  # pylint: disable=unused-argument
    """
    API endpoint to delete a user's account.

    Methods:
        delete(request): Deletes the authenticated user's account.
    """
    user = request.user
    try:
        user.delete()
        return Response({"message": "User account deleted successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": f"Failed to delete account: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
