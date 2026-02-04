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
        "transcript": "Speaker A: Hello\\nSpeaker B: Hi there"
      }
    """
    if not sentences:
        return {"transcript": ""}

    lines = []
    current_speaker = None
    current_chunks = []

    for item in sentences:
        speaker = item.get("speaker") or "Unknown speaker"
        text = item.get("transcript", "")

        # Skip completely empty texts
        if not text:
            continue

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

    human_readable = "\n".join(lines)
    return {"transcript": human_readable}


def get_transcript(meeting_id: str) -> str:
    """Fetch the full transcript for a meeting by ID.

    Uses Bearer token from MEETGEEK_API_KEY. Handles pagination and returns
    a human-readable transcript (speaker-labeled, same-speaker lines merged).
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
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode() if e.fp else ""
            raise RuntimeError(f"MeetGeek API error {e.code}: {body}") from e

        all_sentences.extend(data.get("sentences", []))

        pagination = data.get("pagination", {})
        cursor = pagination.get("next_cursor")
        if not cursor:
            break

    return process_transcript(all_sentences)["transcript"]

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