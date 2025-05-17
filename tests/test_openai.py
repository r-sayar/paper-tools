import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Loads .env file

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("API key not found.")
    exit(1)

response = requests.post(
    "https://api.openai.com/v1/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    json={
        "model": "gpt-3.5-turbo-instruct",
        "prompt": "Say hello world.",
        "max_tokens": 10,
        "temperature": 0.5,
        "n": 1,
        "stop": ["\n"]
    }
)

if response.status_code == 200:
    print("API call successful! Response:")
    print(response.json())
else:
    print("API call failed:")
    print(response.status_code, response.text)