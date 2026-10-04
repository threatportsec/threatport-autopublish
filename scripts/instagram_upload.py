#!/usr/bin/env python3
import os
import json
from pathlib import Path

from instagrapi import Client


SETTINGS_DIR = Path("/tmp/instagrapi_settings")
SETTINGS_DIR.mkdir(exist_ok=True)
SETTINGS_FILE = SETTINGS_DIR / "settings.json"


def get_client() -> Client:
    username = os.environ.get("IG_USERNAME", "")
    password = os.environ.get("IG_PASSWORD", "")
    if not username or not password:
        raise RuntimeError("IG_USERNAME and IG_PASSWORD must be set")

    cl = Client()

    if SETTINGS_FILE.exists():
        try:
            cl.set_settings(json.loads(SETTINGS_FILE.read_text()))
            cl.get_timeline_feed()
            print("  Instagram: restored session from cache")
            return cl
        except Exception:
            print("  Instagram: cached session invalid, logging in fresh")
            SETTINGS_FILE.unlink(missing_ok=True)

    totp_code = os.environ.get("IG_TOTP_CODE", "")
    if totp_code:
        cl.login(username, password, verification_code=totp_code)
    else:
        cl.login(username, password)

    SETTINGS_FILE.write_text(json.dumps(cl.get_settings()))
    print("  Instagram: logged in and cached session")
    return cl


def upload_instagram_reel(video_path: str, caption: str):
    cl = get_client()

    cover_path = os.environ.get("IG_COVER_PATH", "")
    clip = cl.clip_upload(
        video_path=video_path,
        caption=caption,
        extra_data={
            "share_to_facebook": "0",
        },
    )
    print(f"  Instagram reel ID: {clip.pk}")
    return clip.pk


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: instagram_upload.py <video_path> <caption>")
        sys.exit(1)
    upload_instagram_reel(sys.argv[1], sys.argv[2])
