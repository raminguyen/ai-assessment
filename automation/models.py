from openai import OpenAI
from dotenv import load_dotenv
from google import genai
import os
import json
from anthropic import Anthropic
from xai_sdk import Client
from xai_sdk.chat import user, system


load_dotenv()  

chatgpt_api_key=os.getenv("OPENAI_API_KEY")
google_api_key=os.getenv("GOOGLE_API_KEY")
claude_api_key = os.getenv("ANTHROPIC_API_KEY")
grok_api_key = os.getenv("GROK_API_KEY")

def chatgpt(model: str, prompt: str):

    client = OpenAI(api_key=chatgpt_api_key)
    
    response = client.responses.create(
        model=model,
        input=prompt
    )
    
    return response.output_text


def gemini(model: str, prompt: str):
    client = genai.Client(api_key=google_api_key)

    response = client.models.generate_content(
        model=model, 
        contents=prompt

    )

    print(response.text)

    return response.text

def claude(model: str, prompt: str):
    client = Anthropic(api_key=claude_api_key)

    message = client.messages.create(
        model = model,
        max_tokens = 1500,
        messages=[{"role": "user", "content": prompt}]

    )

    return message.content[0].text

def grok(model: str, prompt: str):
    client=Client(
        api_key=grok_api_key,
        timeout=3600
    )

    chat = client.chat.create(model=model)

    chat.append(user(prompt))

    response = chat.sample()

    return response.content

