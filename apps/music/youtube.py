import re
import requests
from django.conf import settings


API_URL = "https://www.googleapis.com/youtube/v3/videos"





def extract_video_id(url):

    patterns = [

        r"v=([^&]+)",

        r"youtu\.be/([^?]+)",

        r"shorts/([^?]+)",

    ]

    for pattern in patterns:

        match = re.search(pattern, url)

        if match:
            return match.group(1)

    return None


def get_video_details(url):

    video_id = extract_video_id(url)

    if not video_id:
        return None

    params = {
        "part": "snippet,contentDetails,statistics",
        "id": video_id,
        "key": settings.YOUTUBE_API_KEY,
    }

    response = requests.get(API_URL, params=params)
    response.raise_for_status()

    data = response.json()

    if not data["items"]:
        return None

    item = data["items"][0]

    return {
        "video_id": video_id,
        "title": item["snippet"]["title"],
        "description": item["snippet"]["description"],
        "channel": item["snippet"]["channelTitle"],
        "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
        "published": item["snippet"]["publishedAt"],
        "duration": item["contentDetails"]["duration"],
        "views": item["statistics"].get("viewCount", 0),
    }