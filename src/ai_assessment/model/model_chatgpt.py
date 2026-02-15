import os
from dotenv import load_dotenv
from openai import OpenAI
from .model import Model

load_dotenv()
chatgpt_api_key = os.getenv("OPENAI_API_KEY")


class ModelChatGPT(Model):
    def __init__(self):
        super().__init__("gpt-5.2-2025-12-11")
        self.client = OpenAI(api_key=chatgpt_api_key)
    
    def api_call(self, prompt):
        response = self.client.responses.create(
            model=self.name,
            input=prompt
        )
        return response.output_text

    def api_call_multi(self, messages):
        input_msgs = []
        for msg in messages:
            input_msgs.append({"role": msg["role"], "content": msg["content"]})
        response = self.client.responses.create(
            model=self.name,
            input=input_msgs
        )
        return response.output_text