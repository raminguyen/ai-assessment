from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()  

api_key=os.getenv("OPENAI_API_KEY")

def chatgpt(model: str, prompt: str):

    client = OpenAI(api_key=api_key)
    
    response = client.responses.create(
        model=model,
        input=prompt
    )
    
    return response.output_text


def gemini(model: str, prompt: str):
    pass

def claude(model: str, prompt: str):
    pass

def copilot(model: str, prompt: str):
    pass