import requests
import os

chatgpt_api_key = os.getenv("OPENAI_API_KEY")

def gpt_5o(prompt, model_name="gpt-5o", max_tokens=1500, temperature=0.7):
    """
    Query GPT-5o with a text prompt.

    Args:
        prompt (str): The text prompt to send.
        model_name (str): Model name (default: 'gpt-5o').
        max_tokens (int): Maximum tokens in the reply.
        temperature (float): Randomness in output (0 = deterministic).

    Returns:
        str: Model's response text or "ERROR: ..." if failed.

    """
    endpoint = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {chatgpt_api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": ""},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    try:
        response = requests.post(endpoint, headers=headers, json=payload)
        result = response.json()

        if "error" in result:
            print("❌ ChatGPT Error:", result["error"]["message"])
            return f"ERROR: {result['error']['message']}"

        return result["choices"][0]["message"]["content"].strip()

    except Exception as e:
        print("❌ Request failed:", e)
        return f"ERROR: {str(e)}"
