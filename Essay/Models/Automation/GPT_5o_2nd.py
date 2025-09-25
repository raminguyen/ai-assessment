# ================== HYPERPARAMS ==================
MODEL_NAME        = "gemini-2.5-flash"
WINDOW_SIZE       = (600, 800)  # kept for reference if your runtime uses it
PROMPTS_JSON_PATH = "/Users/ramihuunguyen/Documents/PhD/AI-Assessment/Essay/Input/prompts1.json"
RUBRIC_JSON_PATH  = "/Users/ramihuunguyen/Documents/PhD/AI-Assessment/Essay/Rubrics/aacu_rubrics.json"
OUT_DIR           = "outputs"
OUT_TXT           = "outputs/combined.txt"
WAIT_STEP1_SEC    = 12
WAIT_STEP2_SEC    = 25
WAIT_STEP3_SEC    = 12
WAIT_STEP4_SEC    = 12
# =================================================

from browser_use import Agent, ChatGoogle
from dotenv import load_dotenv
from pathlib import Path
import os, json, datetime

# env
load_dotenv(dotenv_path=Path(__file__).with_name(".env"))
CHATGPT_EMAIL = os.getenv("CHATGPT_EMAIL")
CHATGPT_PASS  = os.getenv("CHATGPT_PASS")
if not CHATGPT_EMAIL or "example.com" in CHATGPT_EMAIL.lower():
    raise ValueError("CHATGPT_EMAIL is missing or placeholder in .env.")
if not CHATGPT_PASS:
    raise ValueError("CHATGPT_PASS is missing in .env.")

# ensure output dir
Path(OUT_DIR).mkdir(parents=True, exist_ok=True)

# load prompts
with open(PROMPTS_JSON_PATH, "r", encoding="utf-8") as f:
    prompts = json.load(f)
with open(RUBRIC_JSON_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

p1 = f"""{prompts['step1_first_prompt']}"""
p2 = config["step2_scoring_prompt"]  # includes rubric text
p3 = f"""{prompts['step3_revision_prompt']}"""
p4 = f"""{prompts['step4_final_polish_prompt']}"""

# One self-contained task: login + paste+send 4 prompts, waiting after each.
# We instruct the agent to paste (not type) in full; if the site limits length,
# paste in 2–3 chunks then send (Enter). This avoids keystroke timeouts.
task = f"""
Go to https://chatgpt.com
Click "Log in" and sign in with:
- Email: {CHATGPT_EMAIL}
- Password: {CHATGPT_PASS}
Complete any Google redirect if shown.
Wait until the chat input is ready.

In one chat thread, do the following SEQUENTIALLY:

[STEP1]
Paste the FULL text below into the chat box. If it cannot paste in one go, paste in 2–3 chunks in order. Then press Enter to send. Wait ~{WAIT_STEP1_SEC}s for the reply.
<<<STEP1_PROMPT_BEGIN>>>
{p1}
<<<STEP1_PROMPT_END>>>

[STEP2]
Paste the FULL text below (rubric + instruction). If needed, paste in 2–3 chunks in order, then press Enter to send. Wait ~{WAIT_STEP2_SEC}s for the reply.
<<<STEP2_PROMPT_BEGIN>>>
{p2}
<<<STEP2_PROMPT_END>>>

[STEP3]
Paste the FULL text below. If needed, paste in chunks, then press Enter to send. Wait ~{WAIT_STEP3_SEC}s for the reply.
<<<STEP3_PROMPT_BEGIN>>>
{p3}
<<<STEP3_PROMPT_END>>>

[STEP4]
Paste the FULL text below. If needed, paste in chunks, then press Enter to send. Wait ~{WAIT_STEP4_SEC}s for the reply.
<<<STEP4_PROMPT_BEGIN>>>
{p4}
<<<STEP4_PROMPT_END>>>

After STEP4 finishes rendering, scroll through the conversation to ensure the full responses are visible. Then finish.
"""

# run and save
agent = Agent(task=task, llm=ChatGoogle(model=MODEL_NAME))
try:
    history = agent.run_sync()

    # Try to collect all extracted contents from the run
    contents = history.extracted_content() or []
    last = history.final_result()
    if last and (not contents or last != contents[-1]):
        contents.append(last)

    ts = datetime.datetime.now().isoformat(timespec="seconds")
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write(f"=== RUN @ {ts} ===\n\n")
        if contents:
            for i, c in enumerate(contents, 1):
                f.write(f"=== STEP {i} ===\n{c}\n\n")
        else:
            f.write("(no extracted content available)\n")

    print(f"✅ Saved raw text: {OUT_TXT}")

finally:
    # close politely; if your version lacks close_sync, this will no-op
    try:
        agent.close_sync()
    except Exception:
        pass
