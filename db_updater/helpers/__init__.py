import datetime
from typing import Union
import requests


def datetime_to_iso(date: datetime.datetime) -> str:
    date = date - datetime.timedelta(microseconds=date.microsecond)
    return date.isoformat() + "Z"


def iso_increment(date: str) -> str:
    date = datetime.datetime.fromisoformat(date[:-1])
    date = date + datetime.timedelta(seconds=1)
    return datetime_to_iso(date)


def get_videos(
    query: str, publishedAfter: str, key: str = None, limit: int = 50
) -> list:
    if len(query) == 0:
        return []
    if key is None:
        return []

    page_token = None
    videos_retrieved = 0
    videos = []

    if limit <= 0:
        max_results_per_page = 50  # YouTube API allows a maximum of 50 results per page
    else:
        max_results_per_page = min(50, limit)

    while True:
        params = {
            "q": query,
            "key": key,
            "publishedAfter": publishedAfter,
            "maxResults": max_results_per_page,
            "part": "snippet",
            "type": "video",
            "order": "date",
        }

        if page_token:
            params["pageToken"] = page_token

        res = requests.get(
            "https://www.googleapis.com/youtube/v3/search", params=params
        )

        if res.status_code != 200:
            print(res.status_code)
            print(res.json())
            return []

        try:
            data = res.json()
            items = data.get("items", [])
            videos.extend(items)
            videos_retrieved += len(items)
            print(
                f"Retrieved {videos_retrieved}"
                + ("" if limit <= 0 else f"/{limit}")
                + " videos"
            )
            next_page_token = data.get("nextPageToken", None)

            if next_page_token is None or (0 < limit <= videos_retrieved):
                break

            page_token = next_page_token

        except Exception:
            break

    return videos


def get_video_full_description(videoId: str, key: str = None) -> Union[str, None]:
    if key is None:
        raise ValueError("No key provided")
    if len(videoId) != 11:
        raise ValueError("Invalid videoId")

    res = requests.get(
        "https://www.googleapis.com/youtube/v3/videos",
        params={
            "id": videoId,
            "key": key,
            "part": "snippet",
            "fields": "items(snippet/description)",
        },
    )
    if res.status_code != 200:
        print(res.status_code)
        print(res.json())
        return None
    try:
        return (
            None
            if len(items := res.json()["items"]) == 0
            else items[0]["snippet"]["description"]
        )
    except Exception as e:
        print("error")
        return None
