"""
Fetch contacts from Supabase via the get_unique_hubspot_attendees RPC.
"""
import json
import os
import urllib.request
import urllib.error


SUPABASE_URL = "https://uhvcbstdykcvgmzqpvpd.supabase.co"
RPC_NAME = "get_unique_hubspot_attendees"


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
 