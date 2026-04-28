import httpx

API_KEY = "AIzaSyDmjOJeymLA5M6meKrjxwTHByJlnqJKgCw"

# List models
r = httpx.get(f"https://generativelanguage.googleapis.com/v1/models?key={API_KEY}")
print("Models status:", r.status_code)
if r.status_code == 200:
    models = r.json().get("models", [])
    gemini_models = [m["name"] for m in models if "gemini" in m["name"].lower()]
    print("Gemini models:")
    for m in gemini_models[:5]:
        print(f"  {m}")
else:
    print("Error listing models:", r.text)
