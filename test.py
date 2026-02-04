from generate_ids import generate_names
from meetgeek import get_all_meetings
# rv = generate_names("e42780a6-eb7e-4852-87ed-53fcdbda929a")
# print(rv)
# exit()

meetings = get_all_meetings()
for meeting in meetings:
    print(meeting['meeting_id'])
    response = generate_names(meeting['meeting_id'])
    print(response)