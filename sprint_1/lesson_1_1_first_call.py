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

# 4. Define the JSON Request Payload
payload = {
    "model": "openai/gpt-oss-20b:free",
    "messages": [
        {"role": "user", "content": "Explain the concept of Agentic AI in one sentence."}
    ]
}

# 5. Compile and Execute the HTTP Request
data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(url, data=data, headers=headers, method="POST")

try:
    print("Sending request to OpenRouter...")
    with urllib.request.urlopen(req) as response:
        # Read the raw byte response
        raw_response = response.read()
        
        # Decode bytes and parse to a Python dictionary
        result = json.loads(raw_response.decode("utf-8"))
        
        # Extract the model's text response content
        ai_response = result["choices"][0]["message"]["content"]
        
        # Extract token consumption data
        prompt_tokens = result["usage"]["prompt_tokens"]
        completion_tokens = result["usage"]["completion_tokens"]
        
        # Print results
        print("\n=== Response ===")
        print(ai_response)
        print("================")
        print(f"Prompt Tokens: {prompt_tokens}")
        print(f"Response Tokens: {completion_tokens}")

except Exception as e:
    print(f"\nAn error occurred while connecting to the API: {e}")
