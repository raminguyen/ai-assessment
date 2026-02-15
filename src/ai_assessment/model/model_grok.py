import os
from dotenv import load_dotenv
from xai_sdk import Client
from xai_sdk.chat import user, assistant
from .model import Model

load_dotenv()
grok_api_key = os.getenv("GROK_API_KEY")


class ModelGrok(Model):
    def __init__(self):
        super().__init__("grok-4-1-fast-reasoning")
        self.client = Client(api_key=grok_api_key, timeout=3600)
    
    def api_call(self, prompt):
        chat = self.client.chat.create(model=self.name)
        chat.append(user(prompt))
        response = chat.sample()
        return response.content

    def api_call_multi(self, messages):
        chat = self.client.chat.create(model=self.name)
        for msg in messages:
            if msg["role"] == "user":
                chat.append(user(msg["content"]))
            else:
                chat.append(assistant(msg["content"]))
        response = chat.sample()
        return response.content