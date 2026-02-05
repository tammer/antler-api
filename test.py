from hubspot import get_contacts_for_owner

contacts = get_contacts_for_owner("29286558")
print(contacts[0])