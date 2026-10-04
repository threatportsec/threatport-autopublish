#!/usr/bin/env python3
"""
One-time setup: run this locally to get a YouTube OAuth2 refresh token.
Requires a Google Cloud project with YouTube Data API v3 enabled and a
Desktop OAuth2 client. Download the client JSON as client_secret.json
in this directory first.

Usage:
    python scripts/get_youtube_token.py
"""
import os
import json
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS = Path(__file__).parent / "client_secret.json"
TOKEN_FILE = Path(__file__).parent / "youtube_token.json"


def main():
    if not CLIENT_SECRETS.exists():
        print("ERROR: Place your client_secret.json next to this script first.")
        print("Get it from Google Cloud Console > APIs & Services > Credentials")
        print("> Create Credentials > OAuth client ID > Desktop app")
        return

    flow = InstalledAppFlow.from_client_secrets_file(
        str(CLIENT_SECRETS), SCOPES
    )
    creds = flow.run_local_server(port=0)

    TOKEN_FILE.write_text(json.dumps({
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
    }))

    print()
    print("=== Copy these into your GitHub repo Secrets ===")
    print(f"YOUTUBE_CLIENT_ID={creds.client_id}")
    print(f"YOUTUBE_CLIENT_SECRET={creds.client_secret}")
    print(f"YOUTUBE_REFRESH_TOKEN={creds.refresh_token}")
    print()
    print(f"Token also saved to {TOKEN_FILE}")


if __name__ == "__main__":
    main()
