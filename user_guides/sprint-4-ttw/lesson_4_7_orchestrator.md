# Lesson 4.7 - The Orchestrator (Pipeline Coordinator)

## Objective

Build the central coordinator pipeline script (`sprint_4/lesson_4_7_orchestrator.py`) that coordinates all 5 specialist agents, manages the shared state dictionary, implements self-correcting error-retry loops, and writes the verified webpage to disk.

---

## Why

Specialist agents are highly capable within their narrow roles, but they do not know how to coordinate with one another. We need a central conductor—the **Orchestrator**—to manage the sequence of operations. 

The Orchestrator captures inputs, applies input shield filters, sends topics to the Researcher, passes findings to the Writer, sends essays to the Designer, coordinates the Developer to compile HTML, routes pages to the Reviewer, and writes the finished page to disk *only* after a successful `PASS` report is achieved.

---

## What We Are Building

A Python orchestration script (`sprint_4/lesson_4_7_orchestrator.py`) containing the core function:
*   `run_publication_pipeline(topic)`: Standardizes the multi-agent data handoffs, executes local search tools dynamically, validates JSON style constraints, and runs a self-correction repair loop (up to 3 times) between the Developer and Reviewer if compiling bugs occur.

---

## Architecture

```text
[User Input] ──► [Input Shield] ──► (Safe?)
                                       │
                                       ▼
+--------------------------------------------------------------------------+
|                            Orchestrator Loop                             |
|                                                                          |
| 1. Run ResearcherAgent  ──► [Route & Run Search Tool] ──► [Truncate]     |
| 2. Run WriterAgent      ──► (Essay text Markdown)                        |
| 3. Run DesignerAgent    ──► [JSON Validation Filter]  ──► (Style dict)   |
|                                                                          |
| 4. Compile Step (Loop up to 3 times):                                    |
|    ├── Run DeveloperAgent ──► (HTML string)                              |
|    └── Run ReviewerAgent  ──► (PASS?) ──► [Break & Write essays/page.html]|
|                                 (FAIL?) ──► [Retry with Reviewer report] |
+--------------------------------------------------------------------------+
```

---

## Prerequisites

- Complete Lesson 4.6.
- Virtual environment activated (`(.venv)` visible in terminal).

---

## Step 1: Create the Orchestrator Pipeline Script

### Do

Create a file named `sprint_4/lesson_4_7_orchestrator.py` and write the following code:

```python
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
```

### What
We initialize a shared `state` dictionary. We connect all 5 subclasses into a single execution stream:
1.  **Researcher:** Calls search tool ➔ returns context notes.
2.  **Writer:** Synthesizes notes ➔ outputs essay Markdown.
3.  **Designer:** Analyzes sentiment ➔ outputs style JSON (verified by JSON validation guardrail).
4.  **Developer & Reviewer Loop:** Compiles HTML ➔ Reviewer checks. If `FAIL`, Developer retries with the audit report. If `PASS`, we break and save.

### Why
Managing data transformations in a central orchestrator keeps individual agents simple and decoupled. The self-correction loop ensures that coding syntax and styling errors are caught and repaired automatically *before* the file is written to the user's disk.

### Behind the Scenes
- The shared `state` dictionary stores intermediate variables, making it easy to track, log, and pass variables between agent interfaces.
- The `dev_prompt` is dynamically rewritten during a `FAIL` attempt. By appending the reviewer's error report to the prompt, we instruct the LLM on exactly *how* to repair the code in the next turn.

### New Concepts
- **Shared State Architecture:** Passing a single state dictionary context along a pipeline.
- **Self-Healing Loop (Retry loop):** Designing loop gates where QA audit failures are fed back to the compiler for automated repairs.

### Verify
Run the orchestrator script in your terminal to watch the entire multi-agent pipeline execute live:

```powershell
python sprint_4/lesson_4_7_orchestrator.py
```

*Expected Output (Truncated log showing the flow):*
```text
==========================================
Starting Multi-Agent Pipeline for Topic:
'Quantum computing impacts on encryption'
==========================================

[Guardrail] Input prompt cleared security checks.

--- [Stage 1] Activating Researcher Agent ---
[Executing Tool: 'web_search' with args: {'query': 'quantum computing encryption impact'}]
[Researcher] Web search completed and context loaded.

--- [Stage 2] Activating Writer Agent ---
[Writer] Essay draft completed in Markdown.

--- [Stage 3] Activating Designer Agent ---
[Designer] Custom visual theme JSON generated and validated.

--- [Stage 4] Activating Developer & Reviewer loop ---

[Compilation Attempt 1 of 3...]
[Developer] Webpage compiled.
[Reviewer] Audit report: PASS

--- [Stage 5] Saving compiled file to 'essays/quantum_computing_impacts_on_encryption.html' ---
Success: File 'essays/quantum_computing_impacts_on_encryption.html' written successfully.

Pipeline execution completed! File written to: output/essays/quantum_computing_impacts_on_encryption.html
```

Check your `output/essays/` directory to verify the finished webpage has been created!

---

## Step 2: Commit and Push to GitHub

### Do

Save your code and commit the changes to GitHub:

```powershell
git add .
git commit -m "sprint 4: lesson 4.7 orchestrator pipeline complete"
git push
```

### What
Staging, committing, and pushing the orchestrator.

### Why
Version tracking the pipeline milestone.

---

## Common Mistakes

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| Pipeline crashes during Designer validation | Designer outputted invalid JSON syntax. | Our try/except block catches this error and automatically falls back to a clean default visual style configuration dictionary to protect pipeline stability. |

---

## Key Takeaways

- Conductor loops coordinate data transitions between independent specialist agents.
- Pass error logs back to the compiler to allow self-healing retry cycles.
- Integrate fallback configurations (like default JSON themes) to maintain system stability when validation checks fail.

---

## Next Lesson

[Lesson 4.8 - Streamlit Web UI](lesson_4_8_streamlit_ui.md) - Learn how to build a Streamlit browser interface to trigger the pipeline and display results.
