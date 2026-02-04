import json
import os

from meetgeek import get_transcript
from groq import get_groq_response
from contact_loader import load_full


NAMES_CACHE_FILE = "names_cache.json"
IDS_CACHE_FILE = "ids_cache.json"


def _load_cache(path: str) -> dict:
    """Load a JSON cache from disk."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        # If cache is corrupted or unreadable, ignore it.
        return {}


def _save_cache(cache: dict, path: str) -> None:
    """Persist a JSON cache to disk."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except OSError:
        # Failing to write cache should not break main flow.
        pass


def generate_names(transcript_id: str) -> str:
    """
    Generate (or retrieve cached) names for a meeting transcript.

    Uses a local JSON cache `names_cache.json` keyed by transcript/meeting id.
    """
    cache = _load_cache(NAMES_CACHE_FILE)

    # Check cache before doing any transcript / LLM work.
    if transcript_id in cache:
        return cache[transcript_id]

    transcript = get_transcript(transcript_id)
    system_prompt = (
        "You will be given a transcript of a meeting. You will need to extract "
        "the full names of the people who were on the call. Only mention the people "
        "who were present. output as a json list of names. output pure json, no markdown or other text."
    )
    user_prompt = transcript
    response = get_groq_response(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    # Store in cache indexed on meeting/transcript id.
    cache[transcript_id] = response
    _save_cache(cache, NAMES_CACHE_FILE)

    return response

def similar_names(name1, name2):
    """Return True if the two names share at least one word (case-insensitive)."""
    words1 = set(name1.lower().split())
    words2 = set(name2.lower().split())
    return bool(words1 & words2)

def filter_names(names,master_list):
    # iterate through masster_list
    shorter_list = []
    for item in master_list:
        for name in names:
            if similar_names(item['name'], name):
                shorter_list.append(item)
                break
    return shorter_list

def generate_ids(transcript_id: str) -> list[str]:
    # First, check the local cache for existing IDs.
    ids_cache = _load_cache(IDS_CACHE_FILE)
    if transcript_id in ids_cache:
        return ids_cache[transcript_id]

    names = generate_names(transcript_id)
    # remove leading ```json and trailing ```
    names = names.replace("```json", "").replace("```", "")
    names_ = json.loads(names)
    print(names_)
    full = load_full()
    filtered_full = filter_names(names_,full)
    system_prompt = (
        f"Consider this list: {names}. You will map each name to a hubspot id based on "
        "the information you are provided that assocates names with hubspot ids. If "
        "names might not match exactly in which case accept a close match. If there is no close match, output null for the hubspot_id. You will output a json "
        "list of FULL NAMES from the mapping data and their hubspot ids. there will be two keys: name and hubspot_id. output pure json, no markdown or other text."
    )
    response = get_groq_response(
        system_prompt=system_prompt,
        user_prompt=json.dumps(filtered_full),
    )
    response = json.loads(response)
    response = [entry for entry in response if entry["hubspot_id"] is not None]

    # Store in cache indexed on meeting/transcript id.
    ids_cache[transcript_id] = response
    _save_cache(ids_cache, IDS_CACHE_FILE)

    return response