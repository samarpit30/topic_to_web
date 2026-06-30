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

# Add a strict System Instruction defining the agent's persona
SYSTEM_INSTRUCTION = (
    "You are a strict, professional Headline Editor. "
    "You must rewrite whatever topic or text the user inputs into a short, compelling "
    "newspaper headline. You must ONLY output the headline string. Do NOT output any "
    "introductory text, conversational comments, or explanations. Do NOT use quotation marks around your headline."
)

# 4. Initialize the stateful conversation history list
messages = []

print("=== Headline Editor Agent Activated ===")
print("Type 'exit' or 'quit' to terminate the session.\n")

# 5. Enter the interactive session loop
while True:
    try:
        # Prompt the user for input
        user_input = input("You: ")
        
        # Check for termination command
        if user_input.strip().lower() in ["exit", "quit"]:
            print("Session terminated. Goodbye!")
            break
            
        # Skip empty entries
        if not user_input.strip():
            continue
            
        # Append the new user message to history
        messages.append({"role": "user", "content": user_input})
        
        # 6. Construct the payload. We inject the System Instruction as the first message
        # using the role "system". This provides the operational guidelines.
        payload = {
            "model": "openai/gpt-oss-20b:free",
            "messages": [
                {"role": "system", "content": SYSTEM_INSTRUCTION}
            ] + messages
        }
        
        # Compile and execute the request
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        
        with urllib.request.urlopen(req) as response:
            raw_response = response.read()
            result = json.loads(raw_response.decode("utf-8"))
            
            # Extract response details
            ai_response = result["choices"][0]["message"]["content"]
            prompt_tokens = result["usage"]["prompt_tokens"]
            completion_tokens = result["usage"]["completion_tokens"]
            
            # Print the AI's response
            print(f"\nAI: {ai_response.strip()}")
            print(f"[Tokens -> Prompt: {prompt_tokens} | Response: {completion_tokens}]\n")
            
            # Append the model's response back to history to maintain context
            messages.append({"role": "assistant", "content": ai_response})

    except Exception as e:
        print(f"\nAn error occurred: {e}\n")
        # Remove the last user message if the request failed to keep memory aligned
        if messages and messages[-1]["role"] == "user":
            messages.pop()
