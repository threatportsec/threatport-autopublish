#!/usr/bin/env python3
import csv
import json
import os
import re
import sys
from datetime import date, datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

TR_TZ = timezone(timedelta(hours=3))
REPO_ROOT = Path(__file__).resolve().parent.parent
VIDEOS_DIR = os.environ.get("VIDEOS_DIR", str(REPO_ROOT))
START_DATE_STR = os.environ.get("START_DATE", "")
METADATA_CSV = Path(VIDEOS_DIR) / "youtube-metadata.csv"


def calculate_day_number():
    if START_DATE_STR:
        start = date.fromisoformat(START_DATE_STR)
    else:
        start = date(2026, 10, 4)
    today = datetime.now(TR_TZ).date()
    return (today - start).days + 1


def load_metadata(day_number):
    with open(METADATA_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row["day"]) == day_number:
                return row
    return None


def load_instagram_caption(day_number):
    folder_pattern = f"{day_number:02d}-*"
    folders = list(Path(VIDEOS_DIR).glob(folder_pattern))
    if not folders:
        return None, None, None

    folder = folders[0]
    publish_md = folder / "publish.md"
    if not publish_md.exists():
        return None, None, None

    content = publish_md.read_text(encoding="utf-8")

    caption_match = re.search(
        r"## Instagram Reels.*?\*\*Caption\*\*\s*```\s*\n(.*?)```",
        content,
        re.DOTALL,
    )
    caption = caption_match.group(1).strip() if caption_match else None

    title_match = re.search(
        r"## YouTube Shorts.*?\*\*Title\*\*.*?```\s*\n(.*?)```",
        content,
        re.DOTALL,
    )
    title = title_match.group(1).strip() if title_match else None

    tags_match = re.search(r"\*\*Tags\*\*:\s*(.*)", content)
    tags = tags_match.group(1).strip() if tags_match else None

    return caption, title, tags


def get_video_path(day_number):
    folder_pattern = f"{day_number:02d}-*"
    folders = list(Path(VIDEOS_DIR).glob(folder_pattern))
    if not folders:
        return None
    mp4s = list(folders[0].glob("*.mp4"))
    return mp4s[0] if mp4s else None


def get_cover_path(day_number):
    folder_pattern = f"{day_number:02d}-*"
    folders = list(Path(VIDEOS_DIR).glob(folder_pattern))
    if not folders:
        return None
    cover = folders[0] / "cover.jpg"
    return cover if cover.exists() else None


def main():
    day = calculate_day_number()
    print(f"Today: {datetime.now(TR_TZ).strftime('%Y-%m-%d')} -> Day {day}")

    if day < 1 or day > 40:
        print(f"Day {day} is outside the 1-40 range. Nothing to publish.")
        return

    meta = load_metadata(day)
    if not meta:
        print(f"No metadata found for day {day}")
        sys.exit(1)

    video_path = get_video_path(day)
    if not video_path:
        print(f"No video file found for day {day}")
        sys.exit(1)

    caption, yt_title, yt_tags = load_instagram_caption(day)

    print(f"Video: {video_path}")
    print(f"YouTube title: {meta['title']}")
    print(f"Instagram caption: {(caption or '')[:80]}...")

    publish_yt = os.environ.get("PUBLISH_YOUTUBE", "true").lower() == "true"
    publish_ig = os.environ.get("PUBLISH_INSTAGRAM", "true").lower() == "true"

    if publish_yt:
        try:
            from youtube_upload import upload_youtube_short
            upload_youtube_short(
                video_path=str(video_path),
                title=meta["title"],
                description=meta["description"],
                tags=yt_tags or "",
            )
            print(f"[OK] YouTube upload complete for day {day}")
        except Exception as e:
            print(f"[FAIL] YouTube upload failed: {e}")
            if os.environ.get("GITHUB_ACTIONS"):
                print(f"::error::YouTube upload failed: {e}")

    if publish_ig:
        try:
            from instagram_upload import upload_instagram_reel
            upload_instagram_reel(
                video_path=str(video_path),
                caption=caption or "",
            )
            print(f"[OK] Instagram upload complete for day {day}")
        except Exception as e:
            print(f"[FAIL] Instagram upload failed: {e}")
            if os.environ.get("GITHUB_ACTIONS"):
                print(f"::error::Instagram upload failed: {e}")


if __name__ == "__main__":
    main()
