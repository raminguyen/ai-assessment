from openai import OpenAI
from dotenv import load_dotenv
from google import genai
import os
import json
from anthropic import Anthropic
from xai_sdk import Client
from xai_sdk.chat import user
import sys
import strip_markdown
from docx import Document
from datetime import datetime


load_dotenv()


class Essay:

  def __init__(self, name):

    self.status = 0
    self.name = name
    self.prompt = None
    self.model = None
    self.essay_text = None
    

  def load_prompt(self, assignment_num=1):

    base_direction = os.path.dirname(os.path.abspath(__file__))

    file_path = os.path.join(base_direction,"prompt.json")

    with open (file_path, 'r') as f:
      data = json.load(f)

    self.write_prompt = data[f"assignment_{assignment_num}_prompt"]
    self.grade_prompt = data["grade_prompt"]
    
    return self.write_prompt, self.grade_prompt

  
  
class Rubric:

  def __init__(self, rubric_type):

    base_direction = os.path.dirname(os.path.abspath(__file__))

    file_path = os.path.join(base_direction,"rubric.json")
    
    with open (file_path, 'r') as f:

      data = json.load(f)

    self.text = data[rubric_type]
    
class Rubric_CriticalThinking:
  
  def __init__(self):
    super().__init__('critical_thinking')
  

class Model:

  def __init__(self, model_name):

    self.name = model_name

    self.client = None

  def generate(self, essay):
    print("Generating an essay")
    print(essay.write_prompt)
    result = self.api_call(essay.write_prompt)
    essay.essay_text = result
    essay.status = 1
    return result
  
  def tune(self, essay, rubric):
    print("Generating a tuned essay using rubric")
    combined_prompt = rubric.text + essay.write_prompt
    result = self.api_call(combined_prompt)
    essay.essay_text = result
    essay.status = 2
    return result
  
  def grade(self, essay, rubric):
    print("Grade an essay")
    combined_prompt = essay.grade_prompt + rubric.text + essay.essay_text
    print(combined_prompt)

    result = self.api_call(combined_prompt)
    essay.grade_result = result
    essay.status = 3
    return result
  
google_api_key = os.getenv("GOOGLE_API_KEY")
chatgpt_api_key=os.getenv("OPENAI_API_KEY")
claude_api_key = os.getenv("ANTHROPIC_API_KEY")
grok_api_key = os.getenv("GROK_API_KEY")

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
  
class ModelClaude(Model):
    def __init__(self):
        super().__init__("claude-sonnet-4-20250514")
        self.client = Anthropic(api_key=claude_api_key)
    
    def api_call(self, prompt):
        message = self.client.messages.create(
            model=self.name,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    
class ModelGrok(Model):
  def __init__(self):
      super().__init__("grok-4-1-fast-reasoning")
      self.client = Client(api_key=grok_api_key, timeout=3600)
  
  def api_call(self, prompt):
      chat = self.client.chat.create(model=self.name)
      chat.append(user(prompt))
      response = chat.sample()
      return response.content

class Util:

  OUTPUT_FOLDER = "results"

  @staticmethod
  def _ensure_folder():
    os.makedirs(Util.OUTPUT_FOLDER, exist_ok=True)

  @staticmethod
  def texttojson(text, file_name, essay, rubric=None, writer_model=None, grader_model=None, source_file=None):
    Util._ensure_folder() 

    data = {
      "essay_name": essay.name,
      "writer_model": writer_model.name if writer_model else None,
      "loaded_from": source_file,
      "grader_model": grader_model.name if grader_model else None,
      "rubric": rubric.text if rubric else None,
      "result": text,
      "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  }
    
    file_path = os.path.join(Util.OUTPUT_FOLDER, file_name)

    with open (file_path, 'w') as f:
      json.dump (data, f, indent=2)

    print("Saved at", file_path)
    
    return file_path


  @staticmethod
  def jsontodoc(json_file, output_name=None):

    json_path = os.path.join(Util.OUTPUT_FOLDER, json_file)

    with open(json_path, "r",) as f:
      data = json.load(f)

    text = data["result"]

    if output_name is None: 
      output_name = json_file.replace(".json", ".docx")

    clean_text = strip_markdown.strip_markdown(text)
    
    doc = Document()

    doc.add_paragraph(clean_text)

    docs_folder = os.path.join(Util.OUTPUT_FOLDER, "docs")

    os.makedirs(docs_folder, exist_ok=True)

    output_path = os.path.join(docs_folder, output_name)

    doc.save(output_path)

    print("Saved at", output_path)

    return output_path

  @staticmethod
  def batch_jsontodoc(json_files):
    for json_file in json_files:
      Util.jsontodoc(json_file)
 
  @staticmethod

  def load_essay(filename):
    base_direction = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_direction, Util.OUTPUT_FOLDER, filename)
    
    with open(file_path, 'r') as f:
      data = json.load(f)
    
    return data["result"]