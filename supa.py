"""
Fetch contacts from Supabase via the get_unique_hubspot_attendees RPC.
"""
import json
import os
import urllib.parse
import urllib.request
import urllib.error


SUPABASE_URL = "https://uhvcbstdykcvgmzqpvpd.supabase.co"
RPC_NAME = "get_unique_hubspot_attendees"


def check_id(id: str) -> bool:
    """Return True if a row exists in the notes table with external_id == id, else False."""
    key = os.environ.get("SUPABASE_SECRET")
    if not key:
        raise RuntimeError("SUPABASE_SECRET environment variable is not set")

    # Query notes table for one row with this external_id
    params = urllib.parse.urlencode({"external_id": f"eq.{id}", "select": "id", "limit": "1"})
    url = f"{SUPABASE_URL}/rest/v1/notes?{params}"
    req = urllib.request.Request(
        url,
        method="GET",
        headers={
            "Content-Type": "application/json",
            "apikey": key,
            "Authorization": f"Bearer {key}",
        },
    )

    try:
        with urllib.request.urlopen(req) as response:
            rows = json.loads(response.read().decode())
            return len(rows) > 0
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"Supabase error {e.code}: {body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Request failed: {e.reason}") from e


def get_contacts_from_supabase() -> list[dict]:
    """Call Supabase RPC get_unique_hubspot_attendees and return the contact rows."""
    key = os.environ.get("SUPABASE_SECRET")
    if not key:
        raise RuntimeError("SUPABASE_SECRET environment variable is not set")

    url = f"{SUPABASE_URL}/rest/v1/rpc/{RPC_NAME}"
    data = json.dumps({}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "apikey": key,
            "Authorization": f"Bearer {key}",
        },
    )

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"Supabase RPC error {e.code}: {body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Request failed: {e.reason}") from e


def get_notes_for_attendee(hubspot_id: str) -> list[dict]:
    """Return notes linked to an attendee hubspot_id, ordered by meeting_at."""
    key = os.environ.get("SUPABASE_SECRET")
    if not key:
        raise RuntimeError("SUPABASE_SECRET environment variable is not set")

    attendee_params = urllib.parse.urlencode({
        "hubspot_id": f"eq.{hubspot_id}",
        "select": "note_id",
    })
    attendee_url = f"{SUPABASE_URL}/rest/v1/attendees?{attendee_params}"
    attendee_req = urllib.request.Request(
        attendee_url,
        method="GET",
        headers={
            "Content-Type": "application/json",
            "apikey": key,
            "Authorization": f"Bearer {key}",
        },
    )

    try:
        with urllib.request.urlopen(attendee_req) as response:
            attendee_rows = json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"Supabase error {e.code}: {body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Request failed: {e.reason}") from e

    note_ids = sorted({row["note_id"] for row in attendee_rows if row.get("note_id") is not None})
    if not note_ids:
        return []

    note_params = urllib.parse.urlencode({
        "id": f"in.({','.join(str(note_id) for note_id in note_ids)})",
        "select": "note,meeting_at,external_id",
        "order": "meeting_at.asc",
    })
    note_url = f"{SUPABASE_URL}/rest/v1/notes?{note_params}"
    note_req = urllib.request.Request(
        note_url,
        method="GET",
        headers={
            "Content-Type": "application/json",
            "apikey": key,
            "Authorization": f"Bearer {key}",
        },
    )

    try:
        with urllib.request.urlopen(note_req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"Supabase error {e.code}: {body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Request failed: {e.reason}") from e


def create_note_with_attendees(
    note_text: str,
    attendees: list[dict],
    meeting_id: str | None = None,
    meeting_at: str | None = None,
) -> int:
    """
    Call Supabase RPC create_note_with_attendees.
    attendees: list of dicts with keys "name" and "hubspot_id".
    Returns the new note id.
    """
    key = os.environ.get("SUPABASE_SECRET")
    if not key:
        raise RuntimeError("SUPABASE_SECRET environment variable is not set")

    url = f"{SUPABASE_URL}/rest/v1/rpc/create_note_with_attendees"
    payload = {
        "note_text": note_text,
        "attendees": attendees,
        "external_id": meeting_id,
    }
    if meeting_at is not None:
        payload["meeting_at"] = meeting_at

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "apikey": key,
            "Authorization": f"Bearer {key}",
        },
    )

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"Supabase RPC error {e.code}: {body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Request failed: {e.reason}") from e
