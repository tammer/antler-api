from generate_names import generate_ids
import json


response = generate_ids("649eb082-39a7-47a2-84ad-1959671920b9")
print(json.dumps(response, indent=4))