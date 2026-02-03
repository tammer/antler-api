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
