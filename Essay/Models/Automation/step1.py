# ================== HYPERPARAMS ==================
PROVIDER          = "claude"  # "chatgpt" | "gemini" | "copilot"
MODEL_NAME        = "gemini-2.5-flash"
WINDOW_SIZE       = (600, 800)
PROMPTS_JSON_PATH = "/Users/ramihuunguyen/Documents/PhD/AI-Assessment/Essay/Input/prompts1.json"
OUT_DIR           = "outputs"
# =================================================

from browser_use import Agent, ChatGoogle
from dotenv import load_dotenv
from pathlib import Path
import os, json, asyncio

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

# --- io paths ---
Path(OUT_DIR).mkdir(parents=True, exist_ok=True)
tag = PROVIDER.lower()
OUT_TXT        = f"{OUT_DIR}/{tag}_step1_draft1.txt"
OUT_RUN_JSON   = f"{OUT_DIR}/{tag}_step1_result.json"
OUT_DRAFT_JSON = f"{OUT_DIR}/{tag}_step1_draft1.json"

# --- prompt ---
with open(PROMPTS_JSON_PATH, "r", encoding="utf-8") as f:
    p1 = str(json.load(f)['step1_first_prompt'])

# --- tasks per provider (short, direct) ---
if PROVIDER == "gemini":
    login_task = f"""
1) Go to {TARGET_URLS['gemini']}
2) Click "Sign in". Use:
   - Email: {EMAIL}
   - Password: {PASS}
3) Wait for compose box.
4) Paste this prompt and send:
   {p1}
5) Grab the response text.
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
5) Grab the response text.
"""
    
else:
    login_task = f"""
1) Go to {TARGET_URLS['chatgpt']}
2) Click "Log in". Use:
   - Email: {EMAIL}
   - Password: {PASS}
3) Wait for chat page. 
4) Paste this prompt and send:
   {p1}
5) Grab the response text.

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
