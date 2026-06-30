# 🚀 Student Prerequisites & Setup Guide
## Multi-Agent AI System Development Workshop

Welcome! To ensure we spend our active workshop hours coding and building our multi-agent content pipeline rather than troubleshooting installations, please complete this guide **before the first session**.

---

## 🛠️ Step 1: Software Installation

### 1. Python 3.10+ (Core Language)
We will write pure Python. You need version **3.10 or higher**.

*   **Windows Installation:**
    1. Download the installer from the [Official Python Website](https://www.python.org/downloads/windows/).
    2. Run the installer.
    3. ⚠️ **IMPORTANT:** Check the box that says **"Add python.exe to PATH"** at the bottom of the installation window before clicking "Install Now".
*   **Mac Installation:**
    1. Install via Homebrew: `brew install python` (recommended), or download the macOS installer from the [Python Downloads Page](https://www.python.org/downloads/macos/).
*   **Verification:** Open your terminal (Mac) or Command Prompt/PowerShell (Windows) and type:
    ```bash
    python --version
    ```
    *It must output `Python 3.10.x` or higher (e.g., `Python 3.11.x`, `Python 3.12.x`).*

---

### 2. Git & GitHub CLI Setup
Git is required to manage our code versioning and link our system to cloud hosting.

*   **Installation:**
    *   **Windows:** Download and install [Git for Windows](https://git-scm.com/download/win).
    *   **Mac:** Run `xcode-select --install` in terminal, or download from [Git for Mac](https://git-scm.com/download/mac).
*   **GitHub Account:**
    *   Sign up for a free account at [github.com](https://github.com/) if you do not have one.
*   **Verification:** Run the following commands to confirm Git is working:
    ```bash
    git --version
    ```

---

### 3. Visual Studio Code (Recommended IDE)
We recommend VS Code for code editing.

1. Download and install [Visual Studio Code](https://code.visualstudio.com/).
2. Open VS Code, go to the Extensions tab on the left sidebar (shortcut: `Ctrl+Shift+X` or `Cmd+Shift+X`).
3. Search for and install the official **Python** extension (published by Microsoft).

---

## 🔑 Step 2: Account Sign-ups & API Keys

### 1. OpenRouter (LLM Access API)
We will route our LLM requests through OpenRouter to access powerful free models (like Google Gemini Flash) without needing credit cards.

1. Go to [openrouter.ai](https://openrouter.ai/) and click **Sign Up** (you can use your Google or GitHub account).
2. Once logged in, navigate to **Keys** in your dashboard (or go to `openrouter.ai/keys`).
3. Click **Create Key**. Give it a name (e.g., `agentic-workshop`), and click **Create**.
4. ⚠️ **Copy the key immediately.** Store it securely in a temporary text file. You will not be able to view it again.

---

### 2. Tavily (Search Engine API for the Researcher Agent)
Our Researcher Agent needs to search the web. We will use Tavily Search API, which offers a generous free tier of 1,000 search queries per month.

1. Go to [tavily.com](https://tavily.com/) and click **Sign Up** (join using your GitHub or Google account).
2. Once in your dashboard, copy the **API Key** shown on your main console screen.
3. Save this key alongside your OpenRouter key.

> 💡 **Fallback (If Tavily doesn't work for you):** 
> Sign up for a free developer account at **Serper** ([serper.dev](https://serper.dev/)) instead. It provides 2,500 free Google search queries. Keep your Serper API key ready in case we need to switch search engines.

