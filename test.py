from generate_ids import generate_ids
import json
from meetgeek import get_all_meetings
from contact_loader import load_full


meetings = get_all_meetings()
# print(json.dumps(meetings, indent=4))

for meeting in meetings:
    print(meeting['meeting_id'])
    response = generate_ids(meeting['meeting_id'])
    print(json.dumps(response, indent=4))