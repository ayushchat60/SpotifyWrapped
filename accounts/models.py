from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
# pylint: disable=E0307
class SpotifyToken(models.Model):
    """
    Model to store the Spotify OAuth token information for a user. This includes
    the access token, refresh token, and expiration time of the access token.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    expires_at = models.DateTimeField()

    def is_expired(self):
        """
        Checks if the Spotify access token has expired.

        Returns:
            bool: True if the token has expired, otherwise False.
        """
        return now() >= self.expires_at


class Artist(models.Model):
    """
    Model to store information about an artist. This includes the artist's name,
    image URL, description, and the top song associated with them.
    """
    name = models.CharField(max_length=255)
    image_url = models.URLField(blank=True, null=True)
    top_song = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    song_preview = models.URLField(blank=True, null=True)

    def __str__(self):
        """
        Returns a string representation of the Artist object.

        Returns:
            str: The name of the artist.
        """
        return self.name


class Track(models.Model):
    """
    Model to store information about a music track. This includes the track's name,
    the artist's name, the album it belongs to, and URLs for previewing and accessing the track.
    """
    name = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    album = models.CharField(max_length=255)
    preview_url = models.URLField(null=True, blank=True)
    track_url = models.URLField()

    def __str__(self):
        """
        Returns a string representation of the Track object.

        Returns:
            str: The name of the track.
        """
        return self.name


class WrappedHistory(models.Model):
    """
    Model to store the user's Spotify wrapped data for a specific year or term. 
    This includes a list of top tracks, artists, and any associated images.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    image = models.URLField(blank=True, null=True)  # Use 'image' instead of 'image_url'
    artists = models.ManyToManyField(Artist)
    created_at = models.DateTimeField(auto_now_add=True)
    tracks = models.ManyToManyField(Track)

    def __str__(self):
        """
        Returns a string representation of the WrappedHistory object.

        Returns:
            str: The title of the wrapped history (e.g., "2023 Wrapped").
        """
        return self.title
