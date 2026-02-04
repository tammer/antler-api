import json
import os

from deduplicate_contacts import deduplicate_contacts
from hubspot import get_contacts_for_owner
from supa import get_contacts_from_supabase


def load_full():
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, "tammer.json")) as f:
        tammer = json.load(f)
    with open(os.path.join(base, "alexa.json")) as f:
        alexa = json.load(f)
    fresh = get_contacts_for_owner("29286558", "2026-02-01T00:00:00.000Z")
    return deduplicate_contacts(fresh + tammer + alexa)


def load_short():
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, "tammer.json")) as f:
        tammer = json.load(f)
    supa = get_contacts_from_supabase()
    fresh = get_contacts_for_owner("29286558", "2026-02-01T00:00:00.000Z")
    return deduplicate_contacts(fresh + tammer + supa)
