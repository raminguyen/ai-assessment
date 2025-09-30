# ================== HYPERPARAMS ==================
MODEL_NAME        = "gemini-2.5-flash"
WINDOW_SIZE       = (600, 800)  # (w, h) optional; kept for consistency
PROMPTS_JSON_PATH = "/Users/ramihuunguyen/Documents/PhD/AI-Assessment/Essay/Input/prompts1.json"
OUT_DIR           = "outputs"
OUT_TXT           = "outputs/step1_draft1.txt"
OUT_JSON          = "outputs/step1_result.json"
# =================================================

from browser_use import Agent, ChatGoogle
from dotenv import load_dotenv
from pathlib import Path
import os, json, datetime

# --- env + safety checks ---
load_dotenv(dotenv_path=Path(__file__).with_name(".env"))
CHATGPT_EMAIL = os.getenv("CHATGPT_EMAIL")
CHATGPT_PASS  = os.getenv("CHATGPT_PASS")
if not CHATGPT_EMAIL or "example.com" in CHATGPT_EMAIL.lower():
    raise ValueError("CHATGPT_EMAIL is missing or placeholder in .env.")
if not CHATGPT_PASS:
    raise ValueError("CHATGPT_PASS is missing in .env.")

# --- ensure local config dir for browser_use (prevents PermissionError) ---
cfg_dir = Path.home() / ".config" / "browseruse"
cfg_dir.mkdir(parents=True, exist_ok=True)

# --- ensure outputs dir ---
Path(OUT_DIR).mkdir(parents=True, exist_ok=True)

# --- load only step 1 prompt ---
with open(PROMPTS_JSON_PATH, "r", encoding="utf-8") as f:
    prompts = json.load(f)
p1 = f"""{prompts['step1_first_prompt']}"""

# --- TASK: Step 1 only (login + first prompt) ---
login_task = f"""
1) Go to https://chatgpt.com
2) Click 'Log in'. Use:
   - Email: {CHATGPT_EMAIL}
   - Password: {CHATGPT_PASS}
   If you see Google sign-in, click Continue and finish sign-in.
3) Wait until the chat page is fully loaded.
4) Paste the following prompt and send to generate Draft 1:
   {p1}
5) Grab the response text.
"""

# --- run agent ---
agent = Agent(
    task=login_task,
    llm=ChatGoogle(model=MODEL_NAME),
)
result = agent.run_sync()

print (result)

agent.close()

draft1 = result
# --- save outputs ---

with open(OUT_TXT, "w", encoding="utf-8") as f:
    f.write(draft1)

