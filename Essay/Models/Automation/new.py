# ================== HYPERPARAMS ==================
MODEL_NAME        = "gemini-2.5-flash"
WINDOW_SIZE       = (600, 800)  # width, height
PROMPTS_JSON_PATH = "/Users/ramihuunguyen/Documents/PhD/AI-Assessment/Essay/Input/prompts1.json"
RUBRIC_JSON_PATH  = "/Users/ramihuunguyen/Documents/PhD/AI-Assessment/Essay/Rubrics/aacu_rubrics.json"
OUT_DIR           = "outputs"
OUT_TXT           = "outputs/step2_result.txt"
COMBINED_JSON     = "outputs/step2_result.json"
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

# Load JSON config containing step2 prompt and rubric
with open(RUBRIC_JSON_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

# unpack prompts
p1 = f"""{prompts['step1_first_prompt']}"""

p2 = config["step2_scoring_prompt"]

login_task = f"""
1) Go to https://chatgpt.com
2) Log in with:
   - Email: {CHATGPT_EMAIL}
   - Password: {CHATGPT_PASS}
3) Wait until the chat page is fully loaded.
4) Find the textarea.

5) In ONE chat thread, send these prompts SEQUENTIALLY (wait for completion each time):

[STEP1] input the first prompt: {p1}. After the first prompt is sent, wait for a response.


[STEP2] Then paste the first half of the second prompt into the textarea: {p2[:len(p2)//2]}. 
Then wait for appending the second half of the second prompt into the same textarea: {p2[len(p2)//2:]} 
Then press Enter to send.

"""

# create agent
agent = Agent(
    task=login_task,
    llm=ChatGoogle(model=MODEL_NAME)
)

# run the agent
history = agent.run_sync()

# grab structured output at the very end
structured = history.structured_output

# ensure output directory exists
os.makedirs(os.path.dirname(OUT_TXT), exist_ok=True)

if structured:
    # save as text
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write(str(structured))

    # save as JSON too, in case you want structured data later
    with open(COMBINED_JSON, "w", encoding="utf-8") as f:
        json.dump(structured.model_dump(), f, ensure_ascii=False, indent=2)

    print(f"✅ Structured output saved: {OUT_TXT}")
    print(f"🎉 Structured JSON saved: {COMBINED_JSON}")
else:
    print("⚠️ No structured output available (final_result or schema missing).")
