import re
import urllib.request
import json

from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.http import JsonResponse

from .models import Feature, Artist, Album, Track, Lyrics


# ── Model admins ───────────────────────────────────────────────────────────────

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'details')
    search_fields = ('name',)


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'genres', 'followers', 'popularity', 'added_at')
    search_fields = ('name', 'genres')
    readonly_fields = ('spotify_id', 'spotify_url', 'added_at')
    list_filter = ('added_at',)


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'type', 'release_date', 'added_at')
    search_fields = ('title', 'artist')
    readonly_fields = ('spotify_id', 'spotify_url', 'added_at')
    list_filter = ('type', 'added_at')


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('name', 'artist', 'album', 'album_ref', 'audio_file', 'popularity', 'added_at')
    search_fields = ('name', 'artist', 'album')
    readonly_fields = ('spotify_id', 'spotify_url', 'duration_ms', 'added_at')
    list_filter = ('added_at',)
    raw_id_fields = ('album_ref',)

@admin.register(Lyrics)
class LyricsAdmin(admin.ModelAdmin):
    list_display = ('name', 'artist', 'track_ref', 'file', 'added_at')

    search_fields = ('name', 'artist',  'track_ref')
    
    readonly_fields = ('id', 'added_at',)

    raw_id_fields = ('track_ref',)


# ── Custom Spotify import views ────────────────────────────────────────────────

def _parse_spotify_url(text):
    text = text.strip()
    m = re.search(r'open\.spotify\.com/(track|album|artist)/([A-Za-z0-9]+)', text)
    if m:
        return m.group(1), m.group(2)
    m = re.match(r'spotify:(track|album|artist):([A-Za-z0-9]+)', text)
    if m:
        return m.group(1), m.group(2)
    if re.match(r'^[A-Za-z0-9]{22}$', text):
        return 'unknown', text
    return None, None


def _fetch_oembed(spotify_url):
    api_url = 'https://open.spotify.com/oembed?url=' + urllib.request.quote(spotify_url, safe='')
    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=6) as resp:
        return json.loads(resp.read().decode())


def spotify_import_view(request):
    url_input = request.GET.get('url', '').strip()
    kind_override = request.GET.get('type', 'track')
    preview = None
    error = None

    if url_input:
        kind, spotify_id = _parse_spotify_url(url_input)
        if kind == 'unknown':
            kind = kind_override

        if not kind or not spotify_id:
            error = 'Could not parse that input. Paste a full Spotify link, e.g. https://open.spotify.com/track/…'
        else:
            canonical_url = f'https://open.spotify.com/{kind}/{spotify_id}'
            try:
                oembed = _fetch_oembed(canonical_url)
                preview = {
                    'kind': kind,
                    'id': spotify_id,
                    'name': oembed.get('title', ''),
                    'image': oembed.get('thumbnail_url', ''),
                    'spotify_url': canonical_url,
                }
            except Exception as exc:
                error = f'Could not fetch Spotify data: {exc}'

    albums = Album.objects.order_by('artist', 'title').values('id', 'title', 'artist', 'cover', 'release_date')

    context = {
        **admin.site.each_context(request),
        'title': 'Import from Spotify',
        'url_input': url_input,
        'kind_override': kind_override,
        'preview': preview,
        'error': error,
        'albums': list(albums),
    }
    return render(request, 'admin/music/spotify_import.html', context)


def spotify_import_save(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    kind = request.POST.get('kind', '').strip()
    spotify_id = request.POST.get('spotify_id', '').strip()
    name = request.POST.get('name', '').strip()
    artist = request.POST.get('artist', '').strip()
    album_name = request.POST.get('album_name', '').strip()
    album_id = request.POST.get('album_id', '').strip()
    image = request.POST.get('image', '').strip()
    spotify_url = request.POST.get('spotify_url', '').strip()
    genres = request.POST.get('genres', '').strip()
    release_date = request.POST.get('release_date', '').strip()
    album_type = request.POST.get('album_type', '').strip()
    audio_file = request.FILES.get('audio_file')

    if not kind or not spotify_id or not name:
        return JsonResponse({'error': 'kind, spotify_id and name are required'}, status=400)

    try:
        if kind == 'track':
            album_ref = None
            if album_id:
                try:
                    album_ref = Album.objects.get(pk=album_id)
                    if not album_name:
                        album_name = album_ref.title
                    if not artist:
                        artist = album_ref.artist
                    if not image:
                        image = album_ref.cover
                    if not release_date:
                        release_date = album_ref.release_date
                except Album.DoesNotExist:
                    pass

            defaults = dict(
                name=name,
                artist=artist,
                album=album_name,
                album_ref=album_ref,
                cover=image,
                spotify_url=spotify_url,
                release_date=release_date,
            )
            if audio_file:
                defaults['audio_file'] = audio_file

            obj, created = Track.objects.update_or_create(
                spotify_id=spotify_id,
                defaults=defaults,
            )
            label = f'{obj.name} — {obj.artist}' if obj.artist else obj.name

        elif kind == 'album':
            obj, created = Album.objects.update_or_create(
                spotify_id=spotify_id,
                defaults=dict(
                    title=name,
                    artist=artist,
                    cover=image,
                    spotify_url=spotify_url,
                    release_date=release_date,
                    type=album_type,
                ),
            )
            label = f'{obj.title} — {obj.artist}' if obj.artist else obj.title

        elif kind == 'artist':
            obj, created = Artist.objects.update_or_create(
                spotify_id=spotify_id,
                defaults=dict(
                    name=name,
                    image=image,
                    spotify_url=spotify_url,
                    genres=genres,
                ),
            )
            label = obj.name

        else:
            return JsonResponse({'error': f'Unknown kind: {kind}'}, status=400)

    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=500)

    return JsonResponse({
        'ok': True,
        'created': created,
        'message': f'{"Added" if created else "Updated"}: {label}',
    })


# ── Inject custom URLs into the default admin site ─────────────────────────────

_orig_get_urls = admin.site.__class__.get_urls


def _patched_get_urls(self):
    custom = [
        path('music/spotify-import/', self.admin_view(spotify_import_view), name='music_spotify_import'),
        path('music/spotify-import/save/', self.admin_view(spotify_import_save), name='music_spotify_import_save'),
    ]
    return custom + _orig_get_urls(self)


admin.site.__class__.get_urls = _patched_get_urls
