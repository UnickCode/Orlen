from django.db import models


class Feature(models.Model):
    name = models.CharField(max_length=100)
    details = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class Artist(models.Model):
    spotify_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    image = models.URLField(blank=True)
    genres = models.CharField(max_length=500, blank=True)
    followers = models.IntegerField(default=0)
    popularity = models.IntegerField(default=0)
    spotify_url = models.URLField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Album(models.Model):
    spotify_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    cover = models.URLField(blank=True)
    release_date = models.CharField(max_length=50, blank=True)
    type = models.CharField(max_length=50, blank=True)
    spotify_url = models.URLField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.title} — {self.artist}"


class Track(models.Model):
    spotify_id = models.CharField(max_length=255, unique=False)
    name = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    album = models.CharField(max_length=255, blank=True)
    album_ref = models.ForeignKey(
        'Album', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='tracks'
    )
    cover = models.URLField(blank=True)
    duration_ms = models.IntegerField(default=0)


    
    preview_url = models.URLField(blank=True, null=True)
    audio_file = models.FileField(upload_to='tracks/', blank=True, null=True)
    popularity = models.IntegerField(default=0)
    spotify_url = models.URLField(blank=True)
    release_date = models.CharField(max_length=50, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.name} — {self.artist}"


class Lyrics(models.Model):
    id = models.CharField(max_length=255, unique=False, primary_key=True)
    name = models.CharField(max_length=255)
    
    artist = models.CharField(max_length=255)
    
    track_ref = models.OneToOneField(
        'Track', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='lyrics'
    )

    file = models.FileField(upload_to='lyrics/') 
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.name} — {self.track_ref}"


    
    
        
# artifacts/django-backend/apps/music/urls.py