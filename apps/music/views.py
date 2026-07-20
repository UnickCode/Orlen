import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import Q
from .models import Feature, Album, Track, Artist
from .spotify import get_auth_manager, get_spotify_client, get_client_credentials_client

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .youtube import get_video_details


def index(request):
    album = Album.objects.all()
    return render(request, "index.html", {"album": album})


# ──────────────────────────────────────────────
# Spotify OAuth
# ──────────────────────────────────────────────


def spotify_login(request):
    next_url = request.GET.get("next", "")
    if next_url:
        request.session["spotify_next"] = next_url
    auth_manager = get_auth_manager(request)
    auth_url = auth_manager.get_authorize_url()
    return redirect(auth_url)


def spotify_callback(request):
    code = request.GET.get("code")
    error = request.GET.get("error")

    if error or not code:
        return JsonResponse({"error": error or "No code returned"}, status=400)

    auth_manager = get_auth_manager(request)
    auth_manager.get_access_token(code)
    next_url = request.session.pop("spotify_next", None)
    return redirect(next_url if next_url else "spotify_profile")


def spotify_logout(request):
    request.session.pop("spotify_token", None)
    return redirect("index")


# ──────────────────────────────────────────────
# Spotify API views
# ──────────────────────────────────────────────


def spotify_profile(request):
    sp = get_spotify_client(request)
    if not sp:
        return redirect("spotify_login")
    profile = sp.current_user()
    return render(request, "music/spotify_profile.html", {"profile": profile})


def _annotate_duration(tracks_list):
    result = []
    for t in tracks_list:
        secs = (t.duration_ms or 0) // 1000
        t.duration_fmt = f"{secs // 60}:{secs % 60:02d}" if secs else ""
        result.append(t)
    return result


def _build_player_queue(tracks_list):
    """Build the JS player queue from the SAME list/order used to render
    the track rows, so QUEUE indices always line up with what's on screen."""
    queue = []
    for t in tracks_list:
        audio_url = t.audio_file.url if t.audio_file else (t.preview_url or "")
        if audio_url:
            queue.append(
                {
                    "id": t.id,
                    "name": t.name,
                    "artist": t.artist,
                    "cover": t.cover or "",
                    "audio_url": audio_url,
                    "duration_ms": t.duration_ms or 0,
                }
            )
    return queue


@require_GET
def spotify_search(request):
    query = request.GET.get("q", "").strip()
    active_tab = request.GET.get("tab", "tracks")

    if query:
        tracks = Track.objects.filter(
            Q(name__icontains=query)
            | Q(artist__icontains=query)
            | Q(album__icontains=query)
        ).order_by("id")
        albums = Album.objects.filter(
            Q(title__icontains=query) | Q(artist__icontains=query)
        )
        artists = Artist.objects.filter(
            Q(name__icontains=query) | Q(genres__icontains=query)
        )
    else:
        tracks = Track.objects.all().order_by("id")
        albums = Album.objects.all()
        artists = Artist.objects.all()

    # Materialize once so the displayed rows and the player queue are
    # built from the exact same ordered list — this keeps Next/Prev/auto-advance
    # in sync with what's shown on screen.
    tracks_list = list(tracks)
    tracks_with_duration = _annotate_duration(tracks_list)
    player_queue = _build_player_queue(tracks_with_duration)

    return render(
        request,
        "music/spotify_search.html",
        {
            "query": query,
            "active_tab": active_tab,
            "tracks": tracks_with_duration,
            "albums": albums,
            "artists": artists,
            "player_queue_json": json.dumps(player_queue),
        },
    )


@require_GET
def album_detail(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    tracks_list = list(Track.objects.filter(album_ref=album).order_by("id"))
    tracks = _annotate_duration(tracks_list)
    player_queue = _build_player_queue(tracks)

    return render(
        request,
        "music/album_detail.html",
        {
            "album": album,
            "tracks": tracks,
            "player_queue_json": json.dumps(player_queue),
        },
    )


@require_GET
def spotify_top_tracks(request):
    sp = get_spotify_client(request)
    if not sp:
        return JsonResponse({"error": "Not authenticated with Spotify"}, status=401)
    time_range = request.GET.get("range", "medium_term")
    top_tracks = sp.current_user_top_tracks(limit=20, time_range=time_range)
    return JsonResponse(top_tracks)


@require_GET
def spotify_recommendations(request):
    sp = get_spotify_client(request)
    if not sp:
        return JsonResponse({"error": "Not authenticated with Spotify"}, status=401)
    seed_tracks = request.GET.get("seed_tracks", "").split(",")
    seed_tracks = [t.strip() for t in seed_tracks if t.strip()][:5]
    if not seed_tracks:
        return JsonResponse({"error": "Provide ?seed_tracks=id1,id2"}, status=400)
    recommendations = sp.recommendations(seed_tracks=seed_tracks, limit=20)
    return JsonResponse(recommendations)


@require_GET
def spotify_new_releases(request):
    sp = get_client_credentials_client()
    releases = sp.new_releases(limit=20)
    return JsonResponse(releases)


# ──────────────────────────────────────────────
# YouTube Import
# ──────────────────────────────────────────────

@staff_member_required
def youtube_import(request):
    return render(request, "admin/music/youtube_import.html")


@staff_member_required
def youtube_import(request):

    preview = None
    error = None
    url = request.GET.get("url", "").strip()

    if request.GET:

        if not url:
            error = "Please enter a YouTube URL."

        else:
            preview = get_video_details(url)

            if not preview:
                error = "Invalid YouTube URL or video could not be found."

    return render(
        request,
        "admin/music/youtube_import.html",
        {
            "preview": preview,
            "url": url,
            "error": error,
        },
    )