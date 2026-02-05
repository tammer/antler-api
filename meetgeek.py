"""
Fetch meeting transcript from MeetGeek API.
"""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone


MEETGEEK_API_KEY = os.environ.get("MEETGEEK_API_KEY")
BASE_URL = "https://api.meetgeek.ai"
PAGE_LIMIT = 500

def get_duration(meeting_id: str) -> int:
    """Get meeting duration in seconds using MeetGeek API (GET /v1/meetings/{meetingId})."""
    api_key = (MEETGEEK_API_KEY or "").strip().strip('"').strip("'")
    if not api_key:
        raise ValueError("MEETGEEK_API_KEY environment variable is not set")

    url = f"{BASE_URL}/v1/meetings/{meeting_id}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "User-Agent": "curl/8.0",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        raise RuntimeError(f"MeetGeek API error {e.code}: {body}") from e

    start_str = data.get("timestamp_start_utc")
    end_str = data.get("timestamp_end_utc")
    if not start_str or not end_str:
        raise ValueError("Meeting response missing timestamp_start_utc or timestamp_end_utc")

    start = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
    end = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)
    return int((end - start).total_seconds())

def process_transcript(sentences: list[dict]) -> dict:
    """
    Takes a list of sentence dictionaries and returns JSON-serialisable data
    containing a human‑readable transcript.

    Expected input format (per item in `sentences`):
      {
        "id": int,
        "transcript": str,
        "timestamp": str,  # ISO-8601, optional for this function
        "speaker": str
      }

    Return value example:
      {
        "transcript": "Speaker A: Hello\\nSpeaker B: Hi there",
        "attendees": ["Speaker A", "Speaker B"]
      }
    """
    if not sentences:
        return {"transcript": "", "attendees": []}

    lines = []
    current_speaker = None
    current_chunks = []
    attendees_seen: list[str] = []  # unique speakers in order of first appearance

    for item in sentences:
        speaker = item.get("speaker") or "Unknown speaker"
        text = item.get("transcript", "")

        # Skip completely empty texts
        if not text:
            continue

        if speaker not in attendees_seen:
            attendees_seen.append(speaker)

        # If this is the same speaker as the previous one, just accumulate text
        if speaker == current_speaker:
            current_chunks.append(text)
        else:
            # Flush previous speaker, if any
            if current_speaker is not None:
                joined = " ".join(current_chunks)
                lines.append(f"{current_speaker}: {joined}")

            # Start tracking new speaker
            current_speaker = speaker
            current_chunks = [text]

    # Flush the last speaker group
    if current_speaker is not None and current_chunks:
        joined = " ".join(current_chunks)
        lines.append(f"{current_speaker}: {joined}")

    # remove "Unknown speaker" from attendees
    attendees_seen = [attendee for attendee in attendees_seen if attendee != "Unknown speaker"]
    attendees_seen = [attendee for attendee in attendees_seen if not attendee.startswith("Speaker_")]
    human_readable = "\n".join(lines)
    return {"transcript": human_readable, "attendees": attendees_seen}


def get_transcript(meeting_id: str) -> dict:
    """Fetch the full transcript for a meeting by ID.

    Uses Bearer token from MEETGEEK_API_KEY. Handles pagination and returns
    a dict with:
      transcript: human-readable transcript (speaker-labeled, same-speaker lines merged)
      attendees: list of speaker names in order of first appearance
    """
    api_key = (MEETGEEK_API_KEY or "").strip().strip('"').strip("'")
    if not api_key:
        raise ValueError("MEETGEEK_API_KEY environment variable is not set")

    all_sentences: list[dict] = []
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
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req) as resp:
                    data = json.loads(resp.read().decode())
                break
            except urllib.error.HTTPError as e:
                body = e.read().decode() if e.fp else ""
                raise RuntimeError(f"MeetGeek API error {e.code}: {body}") from e
            except (urllib.error.URLError, TimeoutError) as e:
                if attempt < 2:
                    time.sleep(5)
                else:
                    raise RuntimeError(f"MeetGeek API request failed after 3 attempts: {e}") from e

        all_sentences.extend(data.get("sentences", []))

        pagination = data.get("pagination", {})
        cursor = pagination.get("next_cursor")
        if not cursor:
            break

    return process_transcript(all_sentences)

def get_all_meetings(token: str | None = None) -> list[dict]:
    """
    Fetch all meetings from MeetGeek API with pagination.
    Returns a list of dicts with meeting_id, timestamp_start_utc, timestamp_end_utc.

    Pass the Bearer token as `token`, or set MEETGEEK_API_TOKEN env var.
    """
    api_token = (token or os.environ.get("MEETGEEK_API_KEY") or "").strip()
    if not api_token:
        raise ValueError("Provide token or set MEETGEEK_API_TOKEN")

    # EU base URL (use api.meetgeek.ai or api-us.meetgeek.ai if needed)
    base_url = "https://api.meetgeek.ai/v1/teams/1843/meetings"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json",
        "User-Agent": "curl/8.0",  # API often blocks Python's default User-Agent
    }

    all_meetings: list[dict] = []
    cursor: str | None = None
    limit = 500  # max per request

    while True:
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        url = f"{base_url}?{urllib.parse.urlencode(params)}"

        req = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            raise RuntimeError(f"MeetGeek API error {e.code}: {body}") from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"Request failed: {e.reason}") from e

        meetings = data.get("meetings") or []
        all_meetings.extend(meetings)

        pagination = data.get("pagination") or {}
        next_cursor = pagination.get("next_cursor")
        if not next_cursor or not meetings:
            break
        cursor = next_cursor

    return all_meetings