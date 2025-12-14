import os
from dotenv import load_dotenv
from google import genai
from .model import Model

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")


class ModelGemini3ProPreview(Model):
    def __init__(self):
        super().__init__("gemini-3-pro-preview")
        self.client = genai.Client(api_key=google_api_key)
    
    def api_call(self, prompt):
        response = self.client.models.generate_content(
            model=self.name,
            contents=prompt
        )
        return response.text