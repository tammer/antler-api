"""Build and print a contact list from HubSpot for a specific owner."""
import json

from deduplicate_contacts import deduplicate_contacts
from hubspot import get_contacts_for_owner

OWNER_ID = "29286558" # Tammer
# OWNER_ID = "607052576" # Alexa

date_limit = "2016-02-01T00:00:00.000Z"


def main():
    contacts = get_contacts_for_owner(OWNER_ID, date_limit)
    contacts = deduplicate_contacts(contacts)
    print(json.dumps(contacts, indent=2))
    return contacts


if __name__ == "__main__":
    main()
