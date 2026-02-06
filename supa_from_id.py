# supa_from_id

from meetgeek import get_stats, get_transcript
import summarize_prompt
from generate_ids import generate_ids
from supa import create_note_with_attendees
from groq import get_groq_response
from supa import check_id

def summarize_transcript(id):
    # load system prompt for summerize_prompt.md from the same directory
    system_prompt = summarize_prompt.system_prompt
    transcript = get_transcript(id)
    ids = generate_ids(id)
    names = [item['name'] for item in ids]
    participants = ", ".join(names)
    user_prompt = f"Participants: {participants}\n\n{transcript['transcript']}"
    response = get_groq_response(system_prompt, user_prompt)
    prepend = f"## Recording\nThis note was created from [this MeetGeek video](https://app2.meetgeek.ai/meeting/{id})\n\n"
    return {"summary": prepend + response, "ids": ids}

def write_to_supa(note_text: str, attendees: list[dict], meeting_id: str | None = None, meeting_at: str | None = None) -> int:
    """Write a note and its attendees to Supabase via create_note_with_attendees. Returns the new note id."""
    return create_note_with_attendees(note_text, attendees, meeting_id=meeting_id, meeting_at=meeting_at)

def supa_from_id(id):
    stats = get_stats(id)
    if stats["duration"] < 300:
        return
    if check_id(id):
        return
    summary = summarize_transcript(id)
    note_id = write_to_supa(summary["summary"], summary["ids"], id, stats["start_time"])
    return {"note_id": note_id, "summary": summary["summary"], "ids": summary["ids"], "stats": stats}