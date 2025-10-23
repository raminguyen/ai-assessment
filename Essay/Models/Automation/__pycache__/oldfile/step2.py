# ================== HYPERPARAMS ==================
PROVIDER          = "gemini"  # "chatgpt" | "gemini" | "copilot"
MODEL_NAME        = "gemini-2.5-flash"
WINDOW_SIZE       = (600, 800)
PROMPTS_JSON_PATH = "/Users/ramihuunguyen/Documents/PhD/AI-Assessment/Essay/Models/Automation/prompts1.json"
OUT_DIR           = "outputs"
GEMINI_DRAFT_PATH = "/Users/ramihuunguyen/Documents/PhD/AI-Assessment/Essay/Models/Automation/essay_extracted.txt"  # text file with extract_structured_data
RUBRIC_PATH       = "/Users/ramihuunguyen/Documents/PhD/AI-Assessment/Essay/Models/Automation/aacu_rubrics.json"

# =================================================

from browser_use import Agent, ChatGoogle, ChatOllama
from dotenv import load_dotenv
from pathlib import Path
import os, json, asyncio
from pathlib import Path
import re

# --- target urls ---
TARGET_URLS = {
    "chatgpt": "https://chatgpt.com",
    "gemini" : "https://gemini.google.com/app",
    "copilot": "https://copilot.microsoft.com/",
    "claude" : "https://claude.ai/login"
}

# --- creds per provider ---
load_dotenv(dotenv_path=Path(__file__).with_name(".env"))
EMAIL = os.getenv("EMAIL")
PASS  = os.getenv("PASS")
if not EMAIL or not PASS:
    raise ValueError(f"{PROVIDER.upper()} email/password missing in .env")

# --- read Gemini draft file ---
essay_text = Path(GEMINI_DRAFT_PATH).read_text(encoding="utf-8")


# --- read AACU rubric JSON: get only the prompt text (no key name) ---
with open(RUBRIC_PATH, "r", encoding="utf-8") as rf:
    rubric_data = json.load(rf)
rubric_text = rubric_data.get("step2_scoring_prompt", "").strip()

# --- load p3 ---
with open(PROMPTS_JSON_PATH, "r", encoding="utf-8") as f:
    p3 = str(json.load(f)['step3_revision_prompt'])

p2 = (essay_text + rubric_text)

def split_into_n(text, n=3):
    L = len(text)
    if L <= 0:
        return [""] * n
    cuts = [round(i * L / n) for i in range(n + 1)]
    return [text[cuts[i]:cuts[i+1]] for i in range(n)]

# --- split and sanity checks ---
parts = split_into_n(p2, 6)
p1_part, p2_part, p3_part, p4_part, p5_part, p6_part = parts

WAIT_BETWEEN_PARTS_SEC = 10
WAIT_AFTER_PARTS_SEC = 15

# --- tasks per provider (short, direct) ---
if PROVIDER == "gemini":
    login_task = f"""

Follow step by step instructions:
    
1) Go to {TARGET_URLS['gemini']} and sign in:
   - Email: {EMAIL}
   - Password: {PASS}

2) Wait for the compose box to be ready.
3) First type {p1_part}. Wait {WAIT_BETWEEN_PARTS_SEC} seconds. Do not key enter yet.
4) Second type {p2_part}. Wait {WAIT_BETWEEN_PARTS_SEC} seconds. Do not key enter yet.
5) Third type {p3_part}. Wait {WAIT_BETWEEN_PARTS_SEC} seconds. Do not key enter yet.
6) Fourth type {p4_part} Wait {WAIT_BETWEEN_PARTS_SEC} seconds. Do not key enter yet. 
7) Fifth type {p5_part}  Wait {WAIT_BETWEEN_PARTS_SEC} seconds. Do not key enter yet.
8) Fifth type {p6_part} Wait {WAIT_BETWEEN_PARTS_SEC} seconds. Then key enter.
9) Wait 45 seconds to ensure response is done.
10) Grab the response text.
11) Next, type following prompt: {p3} and then hit Enter to hit send. 
12) Wait 45 seconds to ensure response is done.
13) Grab the response text.

"""

elif PROVIDER == "copilot":
    login_task = f"""
1) Go to {TARGET_URLS['copilot']}
2) Click the human on the left, then click on "Sign in".  
   Choose **Continue with Google**. Use:
   - Email: {EMAIL}
   - Password: {PASS}
3) Wait until the chat input is ready.
4) Paste this prompt and send:
   {p1}
5) Grab the response text.
"""
    
elif PROVIDER == "claude":
    login_task = f"""
1) Go to {TARGET_URLS['claude']}
2) Click on "Log in".  
   Choose **Continue with Google**. Use:
   - Email: {EMAIL}
   - Password: {PASS}

3) Wait until the chat input box is ready.
4) Paste this prompt and send:
   {p1}
"""
    
else:
    login_task = f"""
1) Go to {TARGET_URLS['chatgpt']}
2) Click "Log in". Use:
   - Email: {EMAIL}
   - Password: {PASS}
3) First type {p1_part} into chatbot (DO NOT PRESS ENTER)
4) Second type {p2_part} into chatbot  (DO NOT PRESS ENTER)
5) Third type {p3_part} into chatbot (DO NOT PRESS ENTER)
6) Enter to send.
7) Grab the response text.
"""
    


# --- helpers ---
def extract_text(agent_history):
    texts = []
    for r in getattr(agent_history, "all_results", []) or []:
        txt = getattr(r, "extracted_content", None)
        if txt: texts.append(txt)
        if hasattr(r, "text") and isinstance(r.text, str): texts.append(r.text)
        if hasattr(r, "content") and isinstance(r.content, str): texts.append(r.content)
    return "\n\n".join(t.strip() for t in texts if t and t.strip()) or str(agent_history)

def dump_json(agent_history):
    try:
        return agent_history.model_dump()
    except Exception:
        try:
            return json.loads(agent_history.model_dump_json())
        except Exception:
            try:
                return json.loads(agent_history.json())
            except Exception:
                return {"string_repr": str(agent_history)}

# --- run ---
agent = Agent(task=login_task, llm=ChatGoogle(model=MODEL_NAME))
result = agent.run_sync()

# --- close ---
try:
    asyncio.run(agent.close())
except RuntimeError:
    import nest_asyncio
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(agent.close())

# --- io paths ---
Path(OUT_DIR).mkdir(parents=True, exist_ok=True)

tag = PROVIDER.lower()

OUT_TXT        = f"{OUT_DIR}/{tag}_ste2_draft1.txt"
OUT_RUN_JSON   = f"{OUT_DIR}/{tag}_step2_result.json"
OUT_DRAFT_JSON = f"{OUT_DIR}/{tag}_step2_draft1.json"

# --- save ---
draft_text = extract_text(result)
with open(OUT_TXT, "w", encoding="utf-8") as f:
    f.write(draft_text)

with open(OUT_DRAFT_JSON, "w", encoding="utf-8") as f:
    json.dump({"provider": PROVIDER, "draft_text": draft_text}, f, ensure_ascii=False, indent=2)

with open(OUT_RUN_JSON, "w", encoding="utf-8") as f:
    json.dump(dump_json(result), f, ensure_ascii=False, indent=2)


print(f"[OK] {PROVIDER} draft saved: {OUT_TXT}")
print(f"[OK] {PROVIDER} draft.json saved: {OUT_DRAFT_JSON}")
print(f".[OK] {PROVIDER} run.json saved: {OUT_RUN_JSON}")
