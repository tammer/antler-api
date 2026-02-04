import json
import os

from meetgeek import get_transcript
from groq import get_groq_response


CACHE_FILE = "names_cache.json"


def _load_cache() -> dict:
    """Load the names cache from disk."""
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        # If cache is corrupted or unreadable, ignore it.
        return {}


def _save_cache(cache: dict) -> None:
    """Persist the names cache to disk."""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    except OSError:
        # Failing to write cache should not break main flow.
        pass


def generate_names(transcript_id: str) -> str:
    """
    Generate (or retrieve cached) names for a meeting transcript.

    Uses a local JSON cache `names_cache.json` keyed by transcript/meeting id.
    """
    cache = _load_cache()

    # Check cache before doing any transcript / LLM work.
    if transcript_id in cache:
        return cache[transcript_id]

    transcript = get_transcript(transcript_id)
    system_prompt = (
        "You will be given a transcript of a meeting. You will need to extract "
        "the names of the people who were on the call. Only mention the people "
        "who were present. output as json list of names."
    )
    user_prompt = transcript
    response = get_groq_response(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    # Store in cache indexed on meeting/transcript id.
    cache[transcript_id] = response
    _save_cache(cache)

    return response
