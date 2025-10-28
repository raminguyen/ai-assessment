# ====================== HYPERPARAMS ======================
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_VERSION = "2023-06-01"
MODEL_NAME = "claude-sonnet-4-20250514"   # Claude Sonnet 4
MAX_TOKENS = 1500
TEMPERATURE = 0.7
# ========================================================

import os, requests

def claude_sonnet4(prompt,
                   model=MODEL_NAME,
                   max_tokens=MAX_TOKENS,
                   temperature=TEMPERATURE):
    """
    One-shot call to Claude Sonnet 4 (Messages API).
    """
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": ANTHROPIC_VERSION,
        "Content-Type": "application/json",
    }
    body = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        r = requests.post(url, headers=headers, json=body, timeout=60)
        j = r.json()
        if r.status_code >= 400 or "error" in j:
            return f"ERROR: {j.get('error', j)}"
        # Claude returns a list of content blocks; join text blocks
        parts = []
        for blk in j.get("content", []):
            if blk.get("type") == "text":
                parts.append(blk.get("text",""))
        return "\n".join(parts).strip()
    except Exception as e:
        return f"ERROR: {e}"
