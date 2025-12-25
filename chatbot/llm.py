import os
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

MODEL = "deepseek/deepseek-chat"


def generate_reply(message: str, history: list) -> str:
    if not OPENROUTER_API_KEY:
        raise ValueError("Missing OPENROUTER_API_KEY")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",  
        "X-Title": "Django Chatbot",
    }

    messages = []
    messages.append({
        "role": "system",
        "content": "You are a helpful chatbot."
    })

    for m in (history or [])[-8:]:
        role = "assistant" if m.get("role") in ("assistant", "bot") else "user"
        messages.append({
            "role": role,
            "content": m.get("content", "")
        })

    messages.append({
        "role": "user",
        "content": message
    })

    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.7,
    }

    response = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=payload,
        timeout=60,
    )

    if response.status_code >= 400:
        raise RuntimeError(
            f"OpenRouter error {response.status_code}: {response.text}"
        )

    data = response.json()
    return data["choices"][0]["message"]["content"].strip()
