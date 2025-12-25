import requests

API_KEY = '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'
API_URL = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",   # or your project URL
    "X-Title": "DeepSeek Test Script"
}

data = {
    "model": "deepseek/deepseek-chat",
    "messages": [
        {"role": "user", "content": "I have sour throat, what should I do?"}
    ]
}

response = requests.post(API_URL, json=data, headers=headers)

if response.status_code == 200:
    print(response.json()["choices"][0]["message"]["content"])
else:
    print("Error:", response.status_code)
    print(response.text)
