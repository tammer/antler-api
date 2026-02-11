from meetgeek import get_all_meetings
from supa_from_id import supa_from_id
from supa import check_id

cut_off = "2026-02-10T00:00:00.000Z"

meetings = get_all_meetings()
for meeting in meetings:
    if meeting["timestamp_start_utc"] < cut_off:
        continue
    print(meeting["meeting_id"])
    if check_id(meeting["meeting_id"]):
        print("Already exists", flush=True)
        continue
    try:
        y = supa_from_id(meeting["meeting_id"])
        print(y['ids'], flush=True)
    except Exception as e:
        print(f"Error processing meeting {meeting['meeting_id']}: {e}", flush=True)
