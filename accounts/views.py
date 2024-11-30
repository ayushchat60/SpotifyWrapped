import os
import json
from datetime import timedelta
from urllib.parse import urlencode

from django.utils.timezone import now
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes

from .models import SpotifyToken, WrappedHistory, Artist, Track
from .serializers import RegisterSerializer, WrappedHistorySerializer
import logging

# Load environment variables
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "username": user.username,
            "email": user.email,
            "spotify_linked": hasattr(user, "spotifytoken"),  # Check if Spotify is linked
        })

class SpotifyAuthView(APIView):
    def get(self, request):
        # Generate Spotify Authorization URL
        url = (
            f"https://accounts.spotify.com/authorize"
            f"?response_type=code&client_id={SPOTIFY_CLIENT_ID}"
            f"&redirect_uri={SPOTIFY_REDIRECT_URI}"
            f"&scope=user-top-read"
        )
        return Response({"url": url}, status=status.HTTP_200_OK)
    
class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "You are authenticated!"})
    

class SpotifyCallbackView(APIView):
    def post(self, request):
        # Ensure the user is authenticated

        user = request.user
        if isinstance(user, AnonymousUser):
            raise PermissionDenied("User is not authenticated.")

        code = request.data.get("code")
        if not code:
            return Response({"error": "No authorization code provided."}, status=400)

        # Debug: Print received code
        print(f"Received Spotify code: {code}")

        # Check if a Spotify token already exists for the user
        existing_token = SpotifyToken.objects.filter(user=user).first()
        if existing_token:
            return Response({"message": "Spotify account already linked."}, status=200)

        # Exchange the code for an access token
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

        # Log Spotify's response
        print(f"Spotify response status: {response.status_code}, body: {response.json()}")

        if response.status_code != 200:
            return Response({"error": response.json().get("error_description", "Unknown error")}, status=400)

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
    permission_classes = [IsAuthenticated]

    def get(self, request, term):
        user = request.user

        # Fetch Spotify Token for the logged-in user
        try:
            spotify_token = SpotifyToken.objects.get(user=user)
        except SpotifyToken.DoesNotExist:
            return Response({"error": "Spotify account not linked."}, status=400)

        headers = {
            "Authorization": f"Bearer {spotify_token.access_token}"
        }
        term_mapping = {
            "short": "short_term",
            "medium": "medium_term",
            "long": "long_term"
        }

        # Spotify endpoint for user's top artists
        url = f"https://api.spotify.com/v1/me/top/artists?time_range={term_mapping.get(term, 'long_term')}&limit=10"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return Response(response.json(), status=200)
        elif response.status_code == 401:  # Token expired
            # Refresh token logic here if needed
            return Response({"error": "Spotify token expired. Please re-link Spotify."}, status=401)
        else:
            return Response({"error": "Failed to fetch Spotify data."}, status=response.status_code)
    
class SpotifyAuthURLView(APIView):
    def get(self, request):
        params = {
            "client_id": SPOTIFY_CLIENT_ID,  # Your Spotify client ID
            "response_type": "code",
            "redirect_uri": SPOTIFY_REDIRECT_URI,  # Redirect URI set in Spotify Developer Dashboard
            "scope": "user-top-read",  # Add more scopes if needed
        }
        url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
        return Response({"url": url}, status=200)
    
class SpotifyLinkCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        spotify_token = SpotifyToken.objects.filter(user=user).first()
        if spotify_token:
            return Response({"linked": True}, status=200)
        return Response({"linked": False}, status=200)
    

class SpotifyWrappedDataView(APIView):
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
            'christmas': 'long_term',  # You can use 'long_term' as fallback
            'halloween': 'long_term',  # Use 'long_term' as fallback
        }

        # Determine which playlists or data to fetch for special terms
        if term == 'christmas' or term == 'halloween':
            # Use specific seasonal playlist logic for Christmas and Halloween
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
    def refresh_spotify_token(self, refresh_token):
        token_url = "https://accounts.spotify.com/api/token"
        response = requests.post(token_url, data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": os.getenv("SPOTIFY_CLIENT_ID"),
            "client_secret": os.getenv("SPOTIFY_CLIENT_SECRET"),
        })
        return response.json()

class WrappedHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        wrapped_history = WrappedHistory.objects.filter(user=user).order_by('-created_at')

        # Format the response
        response_data = [
            {
                "id": history.id,
                "title": history.title,
                "image": history.image,  # Ensure 'image' is used here
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



# Helper function to fetch user top tracks from Spotify API
def fetch_spotify_top_tracks(access_token, time_range):
    url = f"https://api.spotify.com/v1/me/top/tracks?time_range={time_range}&limit=50"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()  # Return the top tracks data
    else:
        raise Exception(f"Spotify API Error: {response.status_code}, {response.text}")

# View to get user tracks based on the time range
def get_user_tracks(request, term):
    access_token = request.headers.get('Authorization')  # Get the access token from the request header

    if not access_token:
        return JsonResponse({"error": "Authorization token is required."}, status=400)

    # Map terms to Spotify time range
    time_range_map = {
        'long': 'long_term',
        'medium': 'medium_term',
        'short': 'short_term',
    }

    if term not in time_range_map:
        return JsonResponse({"error": "Invalid term."}, status=400)

    time_range = time_range_map[term]

    try:
        # Fetch tracks from Spotify
        top_tracks = fetch_spotify_top_tracks(access_token, time_range)
        return JsonResponse(top_tracks, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


#Configure logging
logger = logging.getLogger(__name__)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    user = request.user

    try:
        logger.info(f"Attempting to delete user account: {user.username}")
        user.delete()
        logger.info(f"User account deleted successfully: {user.username}")
        return Response({"message": "User account deleted successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error deleting user account: {str(e)}")
        return Response({"error": f"Failed to delete account: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)