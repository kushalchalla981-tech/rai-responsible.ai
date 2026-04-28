import httpx

API_KEY = "AIzaSyDmjOJeymLA5M6meKrjxwTHByJlnqJKgCw"
url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"

payload = {
    "contents": [{
        "parts": [{"text": "Say hello in 5 words"}]
    }],
    "generationConfig": {
        "temperature": 0.3,
        "maxOutputTokens": 50,
    }
}

resp = httpx.post(url, json=payload, timeout=10.0)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    print(f"Response: {text}")
else:
    print(f"Error: {resp.text}")
