from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class SpotifyToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return now() >= self.expires_at


class Artist(models.Model):
    name = models.CharField(max_length=255)
    image_url = models.URLField(blank=True, null=True)
    top_song = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    song_preview = models.URLField(blank=True, null=True)

class Track(models.Model):
    name = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    album = models.CharField(max_length=255)
    preview_url = models.URLField(null=True, blank=True)
    track_url = models.URLField()

    def __str__(self):
        return self.name
    
class WrappedHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    image = models.URLField(blank=True, null=True)  # Use 'image' instead of 'image_url'
    artists = models.ManyToManyField(Artist)
    created_at = models.DateTimeField(auto_now_add=True)
    tracks = models.ManyToManyField(Track) 