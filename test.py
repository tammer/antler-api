from meetgeek import get_transcript
from groq import get_groq_response

transcript = get_transcript("1e10083d-b10c-482c-902f-546e9a692d18")

system_prompt = "You will be given a transcript of a meeting. You will need to extract the names of the people who were on the call."
user_prompt = transcript

response = get_groq_response(
    system_prompt=system_prompt,
    user_prompt=user_prompt,
)

print(response)