from groq import get_groq_response
import json
from contact_loader import load_short
from make_transcript import make_transcript

response = make_transcript("649eb082-39a7-47a2-84ad-1959671920b9")

# Part 2

system_prompt = f"Consider this list: {response}. You will map each name to a hubspot id based on the information you are provided that assocates names with hubspot ids. If there is no exact mathc, choose the closest match. You will output a json list of FULL NAMES from the mapping date and their hubspot ids. output pure json, no markdown or other text."
user_prompt = json.dumps(load_short())
response = get_groq_response(
    system_prompt=system_prompt,
    user_prompt=user_prompt,
)


response = json.loads(response)
print(json.dumps(response, indent=4))
# remove any entry where hubspot_id is null
response = [entry for entry in response if entry['hubspot_id'] is not None]
print(json.dumps(response, indent=4))