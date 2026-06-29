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

# 4. Intialize the stateful conversation history list
messages = []

print("Chatbot Activated")

while True:
    try:
        # Prompt the user for input
        user_input = input("You: ")

        if not user_input.strip():
            print("Prompt cannot be empty. Please provide a valid prompt.")
            continue

        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the chatbot. Goodbye!")
            break
        
        messages.append({"role": "user", "content": user_input})

        # 6. Build the dynamic payload using the entire message history
        payload = {
            "model": "openai/gpt-oss-20b:free",
            "messages": messages
        }
        


        data = json.dumps(payload).encode('utf-8')

        req = urllib.request.Request(url, data=data, headers=headers)

        print("Sending request to OpenRouter...")
        with urllib.request.urlopen(req) as response:
            # Read he raw byte response
            raw_response = response.read()

            # Decode the byte response to string
            result = json.loads(raw_response.decode('utf-8'))

            # Extract the model's text response content
            ai_response = result["choices"][0]["message"]["content"]

            # Append the AI's response to the message history
            messages.append({"role": "assistant", "content": ai_response})

            print("AI Response:", ai_response)

    except Exception as e:  
        print("Error during API request:", e)

