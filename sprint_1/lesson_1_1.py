import os
import json
import urllib.request
from dotenv import load_dotenv

# 1. Load environment variables from .env file
load_dotenv()

# 2. Get the API key from environment variables
api_key = os.getenv("OPENROUTER_API_KEY")

# 3. Setup OpenRouter Target URL and Headers
url="https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 4. Define the JSON request Payload
payload = {
    "model":"openai/gpt-oss-20b:free",
    "messages":[
        {"role":"user",
        "content":"Explain the concept of multi-agent autonomous systems"}
    ]
}

# 5. Compile and execut the HTTP Request

data = json.dumps(payload).encode('utf-8')

req = urllib.request.Request(url, data=data, headers=headers)

try:
    print("Sending request to OpenRouter...")
    with urllib.request.urlopen(req) as response:
        # Read he raw byte response
        raw_response = response.read()

        # Decode the byte response to string
        result = json.loads(raw_response.decode('utf-8'))

        # Extract the model's text response content
        ai_response = result["choices"][0]["message"]["content"]

        print("AI Response:", ai_response)
except Exception as e:  
    print("Error during API request:", e)

