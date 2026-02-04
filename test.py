from generate_ids import generate_ids
import json
from meetgeek import get_all_meetings
from contact_loader import load_full
from generate_ids import generate_names


meeting_id = "e42780a6-eb7e-4852-87ed-53fcdbda929a"
response = generate_names(meeting_id)
print(response)
exit()
meetings = get_all_meetings()
# print(json.dumps(meetings, indent=4))

for meeting in meetings:
    print(meeting['meeting_id'])
    # response = generate_ids(meeting['meeting_id'])
    # print(json.dumps(response, indent=4))
    response = generate_names(meeting['meeting_id'])
    print(response)
    