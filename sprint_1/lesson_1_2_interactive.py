import os
import json
import urllib.request
from dotenv import load_dotenv

# 1. Load the environment variables from the .env file
load_dotenv()

# 2. Retrieve the OpenRouter API Key
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    print("Error: OPENROUTER_API_KEY not found. Please check your .env file.")
    exit(1)

# 3. Setup OpenRouter Target URL and Headers
url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 4. Accept dynamic input from the user in the terminal
user_prompt = input("Enter a topic for the publication: ")

# Check if the input is empty
if not user_prompt.strip():
    print("Error: Topic input cannot be empty.")
    exit(1)

# 5. Build payload dynamically using the user's input
payload = {
    "model": "openai/gpt-oss-20b:free",
    "messages": [
        {"role": "user", "content": f"Write a short, engaging headline about: {user_prompt}"}
    ]
}

# 6. Compile and Execute the HTTP Request
data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(url, data=data, headers=headers, method="POST")

try:
    print("\nSending request to OpenRouter...")
    with urllib.request.urlopen(req) as response:
        raw_response = response.read()
        result = json.loads(raw_response.decode("utf-8"))
        
        ai_response = result["choices"][0]["message"]["content"]
        prompt_tokens = result["usage"]["prompt_tokens"]
        completion_tokens = result["usage"]["completion_tokens"]
        
        print("\n=== Response ===")
        print(ai_response.strip())
        print("================")
        print(f"Prompt Tokens: {prompt_tokens}")
        print(f"Response Tokens: {completion_tokens}")

except Exception as e:
    print(f"\nAn error occurred while connecting to the API: {e}")
