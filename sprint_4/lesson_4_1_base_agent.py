import os
import json
import urllib.request
from dotenv import load_dotenv

# Load environmental variables locally
load_dotenv()

class Agent:
    def __init__(self, name: str, system_instruction: str, tools: list = None, model: str = "poolside/laguna-m.1:free"):
        """
        Initializes the base agent with a name, system prompt guidelines,
        optional tools, target model, and a private conversation memory list.
        """
        self.name = name
        self.system_instruction = system_instruction
        self.tools = tools or []
        self.model = model
        self.messages = []
        
        # OpenRouter API configurations
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        
        if not self.api_key:
            raise ValueError(f"[{self.name}] Error: OPENROUTER_API_KEY not found in environment variables.")

    def execute(self, user_prompt: str):
        """
        Executes a single conversational turn with the agent.
        Sends the payload to the LLM, updates memory, and returns the response.
        """
        # 1. Append the user prompt to the local memory history
        self.messages.append({"role": "user", "content": user_prompt})
        
        # 2. Setup Headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 3. Build payload. We inject the system instruction at index 0 of the payload
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_instruction}
            ] + self.messages
        }
        
        # 4. If tools are declared, pass them to the API payload
        if self.tools:
            payload["tools"] = self.tools
            
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(self.url, data=data, headers=headers, method="POST")
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                
                message_obj = result["choices"][0]["message"]
                content = message_obj.get("content")
                tool_calls = message_obj.get("tool_calls")
                
                # CASE A: If the agent returns plain text content
                if content and not tool_calls:
                    # Append response to memory to preserve history context
                    self.messages.append({"role": "assistant", "content": content})
                    return content
                    
                # CASE B: If the agent returns a tool execution request
                if tool_calls:
                    # Return the raw message dictionary object so the Orchestrator
                    # routing layer can intercept and execute the requested tool calls
                    return message_obj
                    
        except Exception as e:
            # Revert the last user message if the connection failed to keep memory aligned
            if self.messages and self.messages[-1]["role"] == "user":
                self.messages.pop()
            return f"Error executing agent '{self.name}': {e}"

# --- Local Testing Block ---
if __name__ == "__main__":
    print("=== Testing Base Agent Class ===\n")
    
    # Define a simple Critic Agent to verify inheritance
    critic_persona = (
        "You are a strict critic. Review the user's topic and return "
        "a single, highly critical, analytical sentence. Do not be polite."
    )
    
    try:
        critic_agent = Agent(name="Critic", system_instruction=critic_persona)
        print(f"Agent '{critic_agent.name}' successfully initialized.")
        
        test_topic = "Agentic AI is going to solve all coding tasks."
        print(f"Sending test input: '{test_topic}'...\n")
        response = critic_agent.execute(test_topic)
        
        print("=== Critic Response ===")
        print(response)
        print("=======================")
        
    except Exception as e:
        print(f"Test Failed: {e}")
