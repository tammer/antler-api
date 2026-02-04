import json
import os

from deduplicate_contacts import deduplicate_contacts
from hubspot import get_contacts_for_owner
from supa import get_contacts_from_supabase

us = [
   {
    "hubspot_id": "4",
    "name": "Shambhavi Mishra",
    "email": "Antler"
  },
  {
    "hubspot_id": "5",
    "name": "Tammer Kamel",
    "email": "Antler"
  },
  {
    "hubspot_id": "1",
    "name": "Bernie Li",
    "email": "Antler"
  },
  {
    "hubspot_id": "2",
    "name": "Alex Wright",
    "email": "Antler"
  },
  {
    "hubspot_id": "3",
    "name": "Daphne McLarty",
    "email": "Antler"
  },
  {
    "hubspot_id": "6",
    "name": "Luna Besaiso",
    "email": "Antler"
  }
]


def load_full():
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, "tammer.json")) as f:
        tammer = json.load(f)
    with open(os.path.join(base, "alexa.json")) as f:
        alexa = json.load(f)
    fresh = get_contacts_for_owner("29286558", "2026-02-01T00:00:00.000Z")
    rv = deduplicate_contacts(fresh + tammer + alexa)
    return us + rv


def load_short():
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, "tammer.json")) as f:
        tammer = json.load(f)
    supa = get_contacts_from_supabase()
    fresh = get_contacts_for_owner("29286558", "2026-02-01T00:00:00.000Z")
    return deduplicate_contacts(fresh + tammer + supa)
