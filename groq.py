"""
Call Groq chat completions API directly.
Set GROQ_API_KEY in the environment.
"""
import json
import os
import urllib.error
import urllib.request

GROQ_API_KEY = (os.environ.get("GROQ_API_KEY") or "").strip().strip('"').strip("'")
CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-oss-120b"

def get_groq_response(
    system_prompt: str,
    user_prompt: str,
    model: str = DEFAULT_MODEL,
) -> str:
    """Call Groq chat completions and return the assistant message content."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    body = json.dumps({"model": model, "messages": messages}).encode("utf-8")
    req = urllib.request.Request(
        CHAT_URL,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "curl/7.68.0",
        },
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            err = json.loads(body)
            msg = err.get("error", {}).get("message", body)
        except json.JSONDecodeError:
            msg = body
        raise RuntimeError(f"Groq API error {e.code}: {msg}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Groq request failed: {e}") from e

    choices = data.get("choices")
    if not choices:
        raise RuntimeError("Groq response had no choices")
    content = choices[0].get("message", {}).get("content")
    if content is None:
        raise RuntimeError("Groq response had no message content")
    return content.strip()