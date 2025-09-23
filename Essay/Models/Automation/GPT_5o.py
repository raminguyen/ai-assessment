# ================== HYPERPARAMS ==================
MODEL_NAME        = "gemini-2.5-flash"
WINDOW_SIZE       = (1280, 800)  # width, height
PROMPTS_JSON_PATH = "/Users/ramihuunguyen/Documents/PhD/AI-Assessment/Essay/Input/prompts1.json"
RUBRIC_TXT_PATH   = "/Users/ramihuunguyen/Documents/PhD/AI-Assessment/Essay/Rubrics/aacu_rubrics.txt"
OUT_DIR           = "outputs"
OUT_TXT           = "outputs/combined.txt"
COMBINED_JSON     = "outputs/final_results.json"
# =================================================

from browser_use import Agent, ChatGoogle
from dotenv import load_dotenv
from pathlib import Path
import os, json, re, datetime

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

# load rubric text directly
with open(RUBRIC_TXT_PATH, "r", encoding="utf-8") as f:
    rubric_text = f.read()

# unpack prompts
p1 = prompts["step1_first_prompt"]

p2 = (
    prompts["step2_scoring_prompt"]
    + "\n\n"
    + "Use the following rubric EXACTLY as provided. Do not summarize. Send STEP2 as a single message.\n"
    + "<<<RUBRIC_START>>>\n"
    + "```text\n"
    + rubric_text
    + "\n```"
    + "\n<<<RUBRIC_END>>>"
)

p3 = prompts["step3_revision_prompt"]

p4 = prompts["step4_final_polish_prompt"]

# single chat: send 4 prompts sequentially, then post a combined message
login_task = f"""
1) Go to https://chatgpt.com
2) Click 'Log in'. Use:
   - Email: {CHATGPT_EMAIL}
   - Password: {CHATGPT_PASS}
   If redirected to Google login, click Continue and finish sign-in.
3) Wait until the home/chat page is fully loaded.

4) In ONE chat thread, send these prompts SEQUENTIALLY (wait for completion each time):
   [STEP1] {p1}
   # ✅ IMPORTANT: STEP2 must be posted as ONE message, verbatim, including rubrics.
   [STEP3] {p3}
   [STEP4] {p4}

5) After STEP4 finishes, send ONE final combined message with this exact format:
   ===== BEGIN_COMBINED_RESULTS =====
   --- STEP1 RESPONSE START ---
   (paste full STEP1 answer)
   --- STEP1 RESPONSE END ---

   --- STEP2 RESPONSE START ---
   (paste full STEP2 answer)
   --- STEP2 RESPONSE END ---

   --- STEP3 RESPONSE START ---
   (paste full STEP3 answer)
   --- STEP3 RESPONSE END ---

   --- STEP4 RESPONSE START ---
   (paste full STEP4 answer)
   --- STEP4 RESPONSE END ---
   ===== END_COMBINED_RESULTS =====

6) Post ONLY that combined message as the final output.

7) Save EXACTLY that final combined message into the text file "{Path(OUT_TXT).name}".
"""

agent = Agent(task=login_task, llm=ChatGoogle(model=MODEL_NAME))

history = agent.run_sync()
result  = history.final_result()

if result:
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write(result)

    run_ts = datetime.datetime.now().isoformat(timespec="seconds")

    def grab(block_name):
        pattern = rf"--- {block_name} RESPONSE START ---\s*(.*?)\s*--- {block_name} RESPONSE END ---"
        m = re.search(pattern, result, flags=re.DOTALL | re.IGNORECASE)
        return m.group(1).strip() if m else None

    items = []
    for key, prompt, resp in [
        ("step1_first_prompt", p1, grab("STEP1")),
        ("step2_scoring_prompt", p2, grab("STEP2")),
        ("step3_revision_prompt", p3, grab("STEP3")),
        ("step4_final_polish_prompt", p4, grab("STEP4")),
    ]:
        if resp:
            items.append({"step_key": key, "prompt": prompt, "response": resp})

    with open(COMBINED_JSON, "w", encoding="utf-8") as f:
        json.dump({"run_timestamp": run_ts, "items": items}, f, ensure_ascii=False, indent=4)

    print(f"✅ Saved: {OUT_TXT}")
    print(f"🎉 Combined JSON: {COMBINED_JSON}")
else:
    print("⚠️ No final result received; nothing saved.")
