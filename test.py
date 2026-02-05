# supa_from_id

import os
import json
import urllib.error
import urllib.request

from meetgeek import get_duration, get_transcript
from groq import get_groq_response
import summarize_prompt
from generate_ids import generate_ids
from supa import create_note_with_attendees2

def summarize_transcript(id):
    # load system prompt for summerize_prompt.md from the same directory
    system_prompt = summarize_prompt.system_prompt
    transcript = get_transcript(id)
    ids = generate_ids(id)
    names = [item['name'] for item in ids]
    participants = ", ".join(names)
    print(participants)
    user_prompt = f"Participants: {participants}\n\n{transcript['transcript']}"
    response = get_groq_response(system_prompt, user_prompt)
    return {"summary": response, "ids": ids}

def write_to_supa(note_text: str, attendees: list[dict], created_at: str | None = None) -> int:
    """Write a note and its attendees to Supabase via create_note_with_attendees2. Returns the new note id."""
    return create_note_with_attendees2(note_text, attendees, created_at=created_at)


def supa_from_id(id):
    duration = get_duration(id)
    if duration < 300:
        return
    summary = summarize_transcript(id)
    print(summary['summary'])
    print(summary['ids'])
    note_id = write_to_supa(summary["summary"], summary["ids"])
    print(note_id)

supa_from_id("577074b2-a17e-4817-b9e8-bea0a82ade47")