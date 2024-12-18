"""
This module contains API views and helper functions for managing user accounts,
Spotify authentication, and handling Spotify Wrapped data using Django REST Framework.
"""
# pylint: disable=E0307,W3101,E1101,W0631,W0719,W0718,W0611,W0622
import logging
import os
from datetime import timedelta, datetime
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
    View for user registration. Accepts POST requests with user details,
    validates the input, and creates a new user.
    """
    def post(self, request):  # pylint: disable=unused-argument
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    View for user login. Accepts POST requests with username and password,
    authenticates the user, and returns JWT tokens if successful.
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
    View to retrieve the profile details of the authenticated user.
    Returns username, email, and whether Spotify is linked.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):  # pylint: disable=unused-argument
        user = request.user
        return Response({
            "username": user.username,
            "email": user.email,
            "spotify_linked": hasattr(user, "spotifytoken"),
        })


class SpotifyAuthView(APIView):
    """
    Generates and provides the Spotify authentication URL for users
    to authorize the app with their Spotify account.
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
    Example of a protected API view. Verifies the user's authentication
    and returns a success message if authenticated.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):  # pylint: disable=unused-argument
        return Response({"message": "You are authenticated!"})


class SpotifyCallbackView(APIView):
    """
    Handles the callback from Spotify after user authentication.
    Exchanges the authorization code for access and refresh tokens.
    """
    def post(self, request):  # pylint: disable=unused-argument
        user = request.user
        if isinstance(user, AnonymousUser):
            raise PermissionDenied("User is not authenticated.")

        code = request.data.get("code")
        if not code:
            return Response({"error": "No authorization code provided."}, status=status.HTTP_400_BAD_REQUEST)

        response = requests.post(
            "https://accounts.spotify.com/api/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": SPOTIFY_REDIRECT_URI,
                "client_id": SPOTIFY_CLIENT_ID,
                "client_secret": SPOTIFY_CLIENT_SECRET,
            },
        )

        if response.status_code != 200:
            return Response({"error": response.json().get("error_description", "Unknown error")}, status=status.HTTP_400_BAD_REQUEST)

        data = response.json()
        SpotifyToken.objects.update_or_create(
            user=user,
            defaults={
                "access_token": data["access_token"],
                "refresh_token": data["refresh_token"],
                "expires_at": now() + timedelta(seconds=data["expires_in"]),
            },
        )
        return Response({"message": "Spotify account linked successfully"}, status=200)


class FetchSpotifyWrappedView(APIView):
    """
    Fetches the user's top Spotify artists for a given time period (short, medium, long).
    Requires the user to be authenticated and their Spotify account to be linked.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, term):  # pylint: disable=unused-argument
        user = request.user

        try:
            spotify_token = SpotifyToken.objects.get(user=user)
        except SpotifyToken.DoesNotExist:
            return Response({"error": "Spotify account not linked."}, status=400)

        headers = {"Authorization": f"Bearer {spotify_token.access_token}"}
        term_mapping = {"short": "short_term", "medium": "medium_term", "long": "long_term"}

        url = f"https://api.spotify.com/v1/me/top/artists?time_range={term_mapping.get(term, 'long_term')}&limit=10"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return Response(response.json(), status=200)
        elif response.status_code == 401:
            return Response({"error": "Spotify token expired. Please re-link Spotify."}, status=401)
        return Response({"error": "Failed to fetch Spotify data."}, status=response.status_code)


class SpotifyAuthURLView(APIView):
    """
    Provides a URL for Spotify authentication with the required scopes.
    """
    def get(self, request):  # pylint: disable=unused-argument
        params = {
            "client_id": SPOTIFY_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": SPOTIFY_REDIRECT_URI,
            "scope": "user-top-read",
        }
        url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
        return Response({"url": url}, status=200)


class SpotifyLinkCheckView(APIView):
    """
    Checks whether the authenticated user's Spotify account is linked.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):  # pylint: disable=unused-argument
        user = request.user
        spotify_token = SpotifyToken.objects.filter(user=user).first()
        return Response({"linked": bool(spotify_token)}, status=200)

    
class SpotifyWrappedDataView(APIView):
    """
    Fetches and stores the user's Spotify wrapped data (top artists and tracks)
    for a specific term (short, medium, long, christmas, halloween).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, term): 
        # Validate term
        if term not in ['short', 'medium', 'long', 'christmas', 'halloween']:
            return Response({"error": "Invalid term"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve user's Spotify token
        user = request.user
        try:
            spotify_token = SpotifyToken.objects.get(user=user)
        except SpotifyToken.DoesNotExist:
            return Response({"error": "Spotify account not linked."}, status=status.HTTP_400_BAD_REQUEST)

        # Refresh token if expired
        if spotify_token.expires_at <= now():
            token_response = self.refresh_spotify_token(spotify_token.refresh_token)
            if "error" in token_response:
                return Response({"error": "Failed to refresh Spotify token."}, status=status.HTTP_400_BAD_REQUEST)
            spotify_token.access_token = token_response["access_token"]
            spotify_token.expires_at = now() + timedelta(seconds=token_response["expires_in"])
            spotify_token.save()

        # Map terms to Spotify API time ranges or custom logic for Christmas/Halloween
        time_range_mapping = {
            'short': 'short_term',
            'medium': 'medium_term',
            'long': 'long_term',
            'christmas': self.get_christmas_time_range(),  # Custom function to get the Christmas time range
            'halloween': self.get_halloween_time_range(),  # Custom function to get the Halloween time range
        }

        # Determine the correct API URL based on the term
        if term == 'christmas' or term == 'halloween':
            # These terms use specific seasonal playlists or time ranges
            artists_api_url = f"https://api.spotify.com/v1/me/top/artists?time_range={time_range_mapping[term]}&limit=10"
            tracks_api_url = f"https://api.spotify.com/v1/me/top/tracks?time_range={time_range_mapping[term]}&limit=50"
        else:
            # Default behavior for short, medium, and long term wrapped
            artists_api_url = f"https://api.spotify.com/v1/me/top/artists?time_range={time_range_mapping[term]}&limit=10"
            tracks_api_url = f"https://api.spotify.com/v1/me/top/tracks?time_range={time_range_mapping[term]}&limit=50"

        # Fetch data from Spotify API
        artists_response = requests.get(artists_api_url, headers={"Authorization": f"Bearer {spotify_token.access_token}"})
        tracks_response = requests.get(tracks_api_url, headers={"Authorization": f"Bearer {spotify_token.access_token}"})

        if artists_response.status_code == 200 and tracks_response.status_code == 200:
            artists_data = artists_response.json()
            tracks_data = tracks_response.json()

            # Save Wrapped history
            wrapped_history = WrappedHistory.objects.create(
                user=user,
                title=f"{term.capitalize()}-Term Wrapped",
                image=artists_data["items"][0]["images"][0]["url"] if artists_data["items"] and artists_data["items"][0]["images"] else "",
            )

            # Save top artists
            for artist_data in artists_data["items"]:
                artist = Artist.objects.create(
                    name=artist_data["name"],
                    image_url=artist_data["images"][0]["url"] if artist_data["images"] else "",
                    description=", ".join(artist_data.get("genres", [])) if artist_data.get("genres") else "No genre available",
                    song_preview=artist_data.get("external_urls", {}).get("spotify", ""),
                )

                top_song_id = None
                for track_data in tracks_data["items"]:
                    if any(artist.name == track_artist["name"] for track_artist in track_data["artists"]):
                        top_song_id = track_data["id"]
                        break

                if top_song_id:
                    song_preview_url = f"https://open.spotify.com/track/{top_song_id}"
                    artist.song_preview = song_preview_url
                    artist.top_song = track_data["name"]
                    artist.save()

                wrapped_history.artists.add(artist)

            wrapped_history.save()

            # Save tracks
            for track_data in tracks_data["items"]:
                track = Track.objects.create(
                    name=track_data["name"],
                    artist=", ".join([artist["name"] for artist in track_data["artists"]]),
                    album=track_data["album"]["name"],
                    preview_url=track_data["preview_url"],
                    track_url=track_data["external_urls"]["spotify"]
                )
                wrapped_history.tracks.add(track)

            wrapped_history.save()

            # Return structured response
            wrapped_data = {
                'artists': [
                    {
                        'id': artist['id'],
                        'name': artist['name'],
                        'genres': artist.get('genres', []),
                        'image': artist['images'][0]['url'] if artist['images'] else None,
                        'popularity': artist['popularity']
                    }
                    for artist in artists_data['items']
                ],
                'tracks': [
                    {
                        'id': track['id'],
                        'name': track['name'],
                        'album': track['album']['name'],
                        'album_image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                        'artists': [{'id': artist['id'], 'name': artist['name']} for artist in track['artists']],
                        'preview_url': track['preview_url'],
                        'popularity': track['popularity']
                    }
                    for track in tracks_data['items']
                ]
            }

            return Response(wrapped_data, status=status.HTTP_200_OK)
        
        else:
            return Response({
                "error": "Failed to fetch Spotify data.",
                "artist_details": artists_response.json(),
                "track_details": tracks_response.json()
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def get_christmas_time_range(self):
        """
        Defines the time range for Christmas (e.g., from Dec 1 to Dec 31).
        This can be customized to fit the specific date range you'd like to fetch.
        """
        current_date = datetime.now()
        if current_date.month == 12:
            return 'short_term'  # Default long-term range; can adjust if needed
        return 'long_term'  # Fallback

    def get_halloween_time_range(self):
        """
        Defines the time range for Halloween (e.g., from Oct 1 to Oct 31).
        """
        current_date = datetime.now()
        if current_date.month == 10:
            return 'short_term'  # Example, could adjust as necessary
        return 'medium_term'  # Fallback
class WrappedHistoryView(APIView):
    """
    Retrieves the Spotify wrapped history for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):  # pylint: disable=unused-argument
        user = request.user
        wrapped_history = WrappedHistory.objects.filter(user=user).order_by('-created_at')

        response_data = [
            {
                "id": history.id,
                "title": history.title,
                "image": history.image,
                "artists": [
                    {
                        "name": artist.name,
                        "images": [{"url": artist.image_url}],
                        "top_song": artist.top_song,
                        "description": artist.description,
                        "song_preview": artist.song_preview,
                    }
                    for artist in history.artists.all()
                ],
            }
            for history in wrapped_history
        ]

        return Response(response_data, status=200)


def fetch_spotify_top_tracks(access_token, time_range):
    """
    Fetches the user's top tracks from Spotify based on the specified time range.

    Args:
        access_token (str): Spotify API access token.
        time_range (str): Time range for the top tracks (e.g., 'short_term').

    Returns:
        dict: JSON response containing the top tracks data.

    Raises:
        Exception: If the Spotify API returns an error.
    """
    url = f"https://api.spotify.com/v1/me/top/tracks?time_range={time_range}&limit=50"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    raise Exception(f"Spotify API Error: {response.status_code}, {response.text}")


def get_user_tracks(request, term):  # pylint: disable=unused-argument
    """
    Retrieves the user's top tracks for a specified time range.

    Args:
        request (HttpRequest): The HTTP request object containing headers with the access token.
        term (str): The time range term ('short', 'medium', 'long').

    Returns:
        JsonResponse: JSON response containing the top tracks or an error message.
    """
    access_token = request.headers.get('Authorization')
    if not access_token:
        return JsonResponse({"error": "Authorization token is required."}, status=400)

    time_range_map = {'long': 'long_term', 'medium': 'medium_term', 'short': 'short_term'}
    if term not in time_range_map:
        return JsonResponse({"error": "Invalid term."}, status=400)

    try:
        top_tracks = fetch_spotify_top_tracks(access_token, time_range_map[term])
        return JsonResponse(top_tracks, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):  # pylint: disable=unused-argument
    """
    Deletes the authenticated user's account.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        Response: A success message or an error message in case of failure.
    """
    user = request.user

    try:
        user.delete()
        return Response({"message": "User account deleted successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": f"Failed to delete account: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_wrap(request, id):  # pylint: disable=unused-argument
    """
    Deletes the authenticated user's wrap.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        Response: A success message or an error message in case of failure.
    """
    wrap = WrappedHistory.objects.get(pk=id)

    try:
        wrap.delete()
        return Response({"message": "Wrap deleted successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": f"Failed to delete wrap: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)