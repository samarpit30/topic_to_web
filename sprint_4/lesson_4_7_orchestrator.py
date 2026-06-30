import os
import sys
import json
import time
from dotenv import load_dotenv

# Ensure parent directory is in path so we can import sibling modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our working tools and validation guardrails from Sprint 2
from sprint_2.lesson_2_1_web_search import web_search
from sprint_2.lesson_2_2_file_io import write_file
from sprint_2.lesson_2_3_guardrails import input_shield, truncate_text
from sprint_2.lesson_2_4_json_validation import validate_designer_json

# Import all 5 specialist agent subclasses from Sprint 4
from sprint_4.lesson_4_2_researcher import ResearcherAgent
from sprint_4.lesson_4_3_writer import WriterAgent
from sprint_4.lesson_4_4_designer import DesignerAgent
from sprint_4.lesson_4_5_developer import DeveloperAgent
from sprint_4.lesson_4_6_reviewer import ReviewerAgent

# Load environment variables
load_dotenv()

def run_publication_pipeline(topic: str) -> str:
    """
    Coordinates the multi-agent pipeline from topic to final compiled,
    verified HTML page inside output/essays/.
    """
    # Initialize the shared state dictionary to pass data between agents
    state = {
        "topic": topic,
        "research": None,
        "essay": None,
        "design": None,
        "html_code": None,
        "reviewer_report": None
    }
    
    print(f"\n==========================================")
    print(f"Starting Multi-Agent Pipeline for Topic:\n'{topic}'")
    print(f"==========================================\n")
    
    # 0. Check Input Shield Guardrail
    try:
        input_shield(state["topic"])
        print("[Guardrail] Input prompt cleared security checks.")
    except ValueError as e:
        return f"Pipeline Blocked: {e}"
        
    # ----------------------------------------------------
    # STAGE 1: Researcher Agent (Search Tool Calling Loop)
    # ----------------------------------------------------
    time.sleep(1.5)  # Rate limit protection pause
    print("\n--- [Stage 1] Activating Researcher Agent ---")
    researcher = ResearcherAgent()
    
    # Execute the researcher agent
    response = researcher.execute(state["topic"])
    
    # Check if the researcher requested a web search tool call
    if isinstance(response, dict) and "tool_calls" in response:
        tool_call = response["tool_calls"][0]
        args = json.loads(tool_call["function"]["arguments"])
        
        # Execute local search tool
        search_raw = web_search(query=args.get("query"), max_results=args.get("max_results", 3))
        
        # Apply truncation guardrail to keep token limits safe
        state["research"] = truncate_text(search_raw, max_chars=2500)
        print("[Researcher] Web search completed and context loaded.")
    else:
        # Fallback if no tool was called
        state["research"] = response
        print("[Researcher] Completed without search tools.")
        
    # ----------------------------------------------------
    # STAGE 2: Writer Agent (Content Synthesis)
    # ----------------------------------------------------
    time.sleep(1.5)  # Rate limit protection pause
    print("\n--- [Stage 2] Activating Writer Agent ---")
    writer = WriterAgent()
    
    # If research is empty or none, fallback to using the topic directly
    if not state["research"] or state["research"].strip() == "None":
        writer_prompt = f"Write a comprehensive essay directly about this topic: '{state['topic']}'."
    else:
        writer_prompt = f"Write a comprehensive essay using these research notes:\n\n{state['research']}"
    
    state["essay"] = writer.execute(writer_prompt)
    print("[Writer] Essay draft completed in Markdown.")
    
    # ----------------------------------------------------
    # STAGE 3: Designer Agent (Sentiment Analysis & Style JSON)
    # ----------------------------------------------------
    time.sleep(1.5)  # Rate limit protection pause
    print("\n--- [Stage 3] Activating Designer Agent ---")
    designer = DesignerAgent()
    
    raw_design_output = designer.execute(state["essay"])
    
    # Validate and parse the Designer's output using JSON schema checks
    try:
        state["design"] = validate_designer_json(raw_design_output)
        print("[Designer] Custom visual theme JSON generated and validated.")
    except ValueError as e:
        print(f"[Warning] Designer output failed schema validation. Falling back to default theme. Details: {e}")
        # Default design safety fallback
        state["design"] = {
            "detected_sentiment": "default_clean",
            "theme": {
                "background_color": "#ffffff",
                "primary_text": "#333333",
                "accent_color": "#1a73e8",
                "font_family_heading": "sans-serif",
                "font_family_body": "sans-serif"
            },
            "layout_style": "minimalist"
        }
        
    # ----------------------------------------------------
    # STAGE 4: Developer & Reviewer self-correction loop
    # ----------------------------------------------------
    time.sleep(1.5)  # Rate limit protection pause
    print("\n--- [Stage 4] Activating Developer & Reviewer loop ---")
    developer = DeveloperAgent()
    reviewer = ReviewerAgent()
    
    # Set a loop limit of 3 compile retries
    COMPILE_RETRIES = 3
    
    # Construct the initial prompt containing essay and design configs
    dev_prompt = (
        f"Please compile the following content and style guidelines into HTML:\n\n"
        f"=== ESSAY CONTENT ===\n{state['essay']}\n\n"
        f"=== STYLE CONFIGURATION ===\n{json.dumps(state['design'], indent=2)}"
    )
    
    for attempt in range(COMPILE_RETRIES):
        print(f"\n[Compilation Attempt {attempt + 1} of {COMPILE_RETRIES}...]")
        
        # Compile HTML
        state["html_code"] = developer.execute(dev_prompt)
        print("[Developer] Webpage compiled.")
        
        # Run QA Review check
        review_prompt = (
            f"Please audit the following compiled HTML code:\n\n"
            f"=== ORIGINAL ESSAY ===\n{state['essay']}\n\n"
            f"=== STYLE CONFIGURATION ===\n{json.dumps(state['design'])}\n\n"
            f"=== COMPILED HTML ===\n{state['html_code']}"
        )
        
        state["reviewer_report"] = reviewer.execute(review_prompt)
        print(f"[Reviewer] Audit report: {state['reviewer_report'].strip()}")
        
        # Check if audit cleared with PASS
        if "PASS" in state["reviewer_report"]:
            print("[QA Audit] Page successfully verified!")
            break
        else:
            # If FAIL, modify the developer prompt to include the error logs for the next retry
            dev_prompt = (
                f"Your previous HTML compilation failed audit checks. Please fix the bugs listed in this report "
                f"and output the corrected HTML code:\n\n"
                f"=== REVIEWER ERROR REPORT ===\n{state['reviewer_report']}\n\n"
                f"=== PREVIOUS COMPILED HTML ===\n{state['html_code']}"
            )
    else:
        print("\n[Warning] Compile loop reached limit without PASS verification. Proceeding with last build.")
        
    # ----------------------------------------------------
    # STAGE 5: Save File to output directory
    # ----------------------------------------------------
    filename = f"essays/{topic.lower().replace(' ', '_')}.html"
    print(f"\n--- [Stage 5] Saving compiled file to '{filename}' ---")
    
    save_result = write_file(file_path=filename, content=state["html_code"])
    print(save_result)
    
    return f"Pipeline execution completed! File written to: output/{filename}"

# --- Local Testing Block ---
if __name__ == "__main__":
    print("=== Multi-Agent Publication Generator Activated ===")
    print("Type 'exit' or 'quit' to terminate the session.\n")
    
    while True:
        user_topic = input("Enter a topic for your web publication: ")
        
        if user_topic.strip().lower() in ["exit", "quit"]:
            print("Session terminated. Goodbye!")
            break
            
        if not user_topic.strip():
            continue
            
        result = run_publication_pipeline(user_topic)
        print(f"\n{result}\n")
        print("-" * 50)
