import os
from dotenv import load_dotenv
from anthropic import Anthropic
from .model import Model

load_dotenv()
claude_api_key = os.getenv("ANTHROPIC_API_KEY")


class ModelClaude(Model):
    def __init__(self):
        super().__init__("claude-sonnet-4-5-20250929")
        self.client = Anthropic(api_key=claude_api_key)
    
    def api_call(self, prompt):
        message = self.client.messages.create(
            model=self.name,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    def api_call_multi(self, messages):
        message = self.client.messages.create(
            model=self.name,
            max_tokens=2048,
            messages=messages
        )
        return message.content[0].text
    