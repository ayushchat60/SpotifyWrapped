import os
from datetime import timedelta
from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from .models import SpotifyToken  # Ensure this model is defined in your app
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from urllib.parse import urlencode
from .models import WrappedHistory, Artist
from .serializers import WrappedHistorySerializer
from rest_framework.permissions import IsAuthenticated

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
        code = request.data.get("code")
        if not code:
            return Response({"error": "No authorization code provided."}, status=400)

        # Debug: Print received code
        print(f"Received Spotify code: {code}")

        # Check if a Spotify token already exists for the user
        user = request.user
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
        if term not in ['short', 'medium', 'long']:
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

        # Fetch data from Spotify
        time_range_mapping = {'short': 'short_term', 'medium': 'medium_term', 'long': 'long_term'}
        api_url = f"https://api.spotify.com/v1/me/top/artists?time_range={time_range_mapping[term]}&limit=10"
        response = requests.get(api_url, headers={"Authorization": f"Bearer {spotify_token.access_token}"})

        if response.status_code == 200:
            data = response.json()

            # Save Wrapped history
            wrapped_history = WrappedHistory.objects.create(
                user=user,
                title=f"{term.capitalize()}-Term Wrapped",
                image=data["items"][0]["images"][0]["url"] if data["items"] and data["items"][0]["images"] else "",
            )

            for artist_data in data["items"]:
                artist = Artist.objects.create(
                    name=artist_data["name"],
                    image_url=artist_data["images"][0]["url"] if artist_data["images"] else "",
                    top_song=artist_data.get("top_song", "No top song available"),
                    description=", ".join(artist_data.get("genres", [])) if artist_data.get("genres") else "No genre available",
                    song_preview=artist_data.get("external_urls", {}).get("spotify", ""),
                )
                wrapped_history.artists.add(artist)

            wrapped_history.save()

            return Response(data["items"], status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to fetch Spotify data.", "details": response.json()}, status=response.status_code)

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



def get_top_artists_with_personal_top_songs(spotify_token, time_range="short_term", limit=10):
    """Fetch top artists and determine the user's most-played song for each artist."""
    artists_url = f"https://api.spotify.com/v1/me/top/artists?time_range={time_range}&limit={limit}"
    headers = {
        "Authorization": f"Bearer {spotify_token}"
    }
    artists_response = requests.get(artists_url, headers=headers)

    if artists_response.status_code == 200:
        artists = artists_response.json()["items"]
        enriched_artists = []

        for artist in artists:
            artist_data = {
                "name": artist["name"],
                "images": artist["images"],
                "id": artist["id"],
                "description": artist.get("genres", []),
            }

            # Use Spotify's "Get Top Tracks for User" endpoint to fetch user's top songs
            top_tracks_url = f"https://api.spotify.com/v1/me/top/tracks?time_range={time_range}&limit=50"
            tracks_response = requests.get(top_tracks_url, headers=headers)
            if tracks_response.status_code == 200:
                tracks = tracks_response.json().get("items", [])
                # Filter for songs by this artist
                artist_tracks = [track for track in tracks if track["artists"][0]["id"] == artist["id"]]
                if artist_tracks:
                    most_played_track = artist_tracks[0]
                    artist_data["top_song"] = most_played_track["name"]
                    artist_data["song_preview"] = most_played_track.get("preview_url")

            enriched_artists.append(artist_data)

        return enriched_artists
    else:
        return {"error": artists_response.json()}