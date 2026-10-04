#!/usr/bin/env python3
import os
import httplib2
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError


def get_youtube_service():
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN", "")
    if not refresh_token:
        raise RuntimeError("YOUTUBE_REFRESH_TOKEN not set")

    client_id = os.environ.get("YOUTUBE_CLIENT_ID", "775296662158-rs5vh8r3f3f6kqg0n328a1nl0fup7874.apps.googleusercontent.com")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET", "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")

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
    )

    return build("youtube", "v3", credentials=creds)


def upload_youtube_short(video_path: str, title: str, description: str, tags: str):
    youtube = get_youtube_service()

    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tag_list,
            "categoryId": "28",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=10 * 1024 * 1024,
    )

    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  YouTube upload progress: {int(status.progress() * 100)}%")

    video_id = response.get("id", "")
    print(f"  YouTube video ID: {video_id}")
    return video_id


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 5:
        print("Usage: youtube_upload.py <video_path> <title> <description> <tags>")
        sys.exit(1)
    upload_youtube_short(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
