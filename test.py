from generate_ids import generate_ids
import json
from meetgeek import get_all_meetings
from contact_loader import load_full


# def similar_names(name1, name2):
#     """Return True if the two names share at least one word (case-insensitive)."""
#     words1 = set(name1.lower().split())
#     words2 = set(name2.lower().split())
#     return bool(words1 & words2)

# def filter_names(names,master_list):
#     # iterate through masster_list
#     shorter_list = []
#     for item in master_list:
#         for name in names:
#             if similar_names(item['name'], name):
#                 shorter_list.append(item)
#                 break
#     return shorter_list

# master_list = load_full()
# names = ["Alex Wright","Bernie"]
# filtered_names = filter_names(names,master_list)
# print(json.dumps(filtered_names, indent=4))


meetings = get_all_meetings()
# print(json.dumps(meetings, indent=4))

for meeting in meetings:
    print(meeting['meeting_id'])
    response = generate_ids(meeting['meeting_id'])
    print(json.dumps(response, indent=4))