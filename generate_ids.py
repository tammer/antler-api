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
    # system_prompt = (
    #     "You will be given a transcript of a meeting. You will need to extract "
    #     "the full names of the people who were on the call. Only mention the people "
    #     "who were present. output as a json list of names. output pure json, no markdown or other text."
    # )
    # system_prompt = """ You will be given a transcript of a meeting. You will need to extract the full names of the people who were on the call. If the transcript has dialog labeled with speaker names, then you will use those lables to determine the names of the people who were on the call. if the dialog is labled with generic labels such has 'Speaker_01" then read the dialog so see if anyone explicitly sates who is present. do not infer who was present from the dialog. if you can't infer any names then output an empty list. output as a json list of names. output pure json, no markdown or other text.
    # """
    system_prompt = """
    You are an information extraction system.

You will be given a transcript of a meeting.
Your task is to extract the full names of people who were present in the meeting.

Rules:
- If speaker labels contain full human names, include those names. Make sure to include all of the named speakers.
- If speaker labels are generic (e.g. "Speaker_01", "Speaker 2"), then read the dialog to see if someone explicitly states who is present. If someone explicitly states who is present, then include that name in the output. If no one explicitly states who is present, then output an empty list.

Output format:
- Return a JSON array of strings.
- Output pure JSON only. Do not include markdown, comments, or extra text.

    """
    user_prompt = transcript
    response = get_groq_response(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    # Store in cache indexed on meeting/transcript id.
    cache[transcript_id] = response
    # _save_cache(cache, NAMES_CACHE_FILE)

    return response

def similar_names(name1, name2):
    """Return True if any word from name1 is similar to any word from name2 (word contained in word, case-insensitive)."""
    words1 = [w for w in name1.strip().lower().split() if w]
    words2 = [w for w in name2.strip().lower().split() if w]
    if not words1 or not words2:
        return False
    # remove any word less than 2 characters
    words1 = [w for w in words1 if len(w) > 2]
    words2 = [w for w in words2 if len(w) > 2]
    for w1 in words1:
        for w2 in words2:
            shorter, longer = (w1, w2) if len(w1) <= len(w2) else (w2, w1)
            if shorter in longer:
                return True
    return False

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
        "names might not match exactly in which case accept a close match.  If there is no reasonable match, output null for the hubspot_id. You will output a json "
        "list of FULL NAMES from the mapping data and their hubspot ids. there will be two keys: name and hubspot_id. output pure json, no markdown or other text."
    )
    response = get_groq_response(
        system_prompt=system_prompt,
        user_prompt=json.dumps(filtered_full),
    )
    response = json.loads(response)
    response = [entry for entry in response if entry["hubspot_id"] is not None]
    print(response)
    exit()

    # Store in cache indexed on meeting/transcript id.
    ids_cache[transcript_id] = response
    _save_cache(ids_cache, IDS_CACHE_FILE)

    return response