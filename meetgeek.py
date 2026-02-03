"""
Fetch meeting transcript from MeetGeek API.
"""
import json
import os
import urllib.error
import urllib.parse
import urllib.request


MEETGEEK_API_KEY = os.environ.get("MEETGEEK_API_KEY")
BASE_URL = "https://api.meetgeek.ai"
PAGE_LIMIT = 500


def get_transcript(meeting_id: str) -> str:
    """Fetch the full transcript for a meeting by ID.

    Uses Bearer token from MEETGEEK_API_KEY. Handles pagination and returns
    all transcript sentences joined as a single string.
    """
    api_key = (MEETGEEK_API_KEY or "").strip().strip('"').strip("'")
    if not api_key:
        raise ValueError("MEETGEEK_API_KEY environment variable is not set")

    parts: list[str] = []
    cursor: str | None = None

    while True:
        url = f"{BASE_URL}/v1/meetings/{meeting_id}/transcript?limit={PAGE_LIMIT}"
        if cursor:
            url += f"&cursor={urllib.parse.quote(cursor)}"

        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "curl/7.68.0",
            },
            method="GET",
        )
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode() if e.fp else ""
            raise RuntimeError(f"MeetGeek API error {e.code}: {body}") from e

        for s in data.get("sentences", []):
            text = s.get("transcript", "").strip()
            if text:
                parts.append(text)

        pagination = data.get("pagination", {})
        cursor = pagination.get("next_cursor")
        if not cursor:
            break

    return " ".join(parts)
