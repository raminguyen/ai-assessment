from google import genai
import os
import json
import sys
from dotenv import load_dotenv
import strip_markdown
from docx import Document

load_dotenv()

class Essay:

  def __init__(self, name):

    self.status = 0
    self.prompt = None
    self.model = None
    self.essay_text = None
    self.name = name

  def load_prompt(self):

    base_direction = os.path.dirname(os.path.abspath(__file__))

    file_path = os.path.join(base_direction,"prompt.json")

    with open (file_path, 'r') as f:

      data = json.load(f)

    self.write_prompt = data["assignment_1_prompt"]
    self.grade_prompt = data["grade_prompt"]
    
    return self.write_prompt, self.grade_prompt

  def load_essay(self):
    base_direction = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_direction,"assignment1.json")

    with open (file_path, 'r') as f:
      data = json.load(f)

    self.essay_text = data["essay"]

    return self.essay_text
  
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
    
API_KEY = os.getenv("GOOGLE_API_KEY")

class Model:

  def __init__(self, model_name):

    self.name = model_name

    self.client = None # what calls the API

  def generate(self,essay, rubric):
    
    pass

  def tune(self, essay, rubric):
    pass

  def grade(self, essay, rubric):
    pass


class ModelGemini3ProPreview(Model):

  def __init__(self):

    super().__init__("gemini-3-pro-preview")

    self.client = genai.Client(api_key=API_KEY)

  def geminiapi(self, prompt):

    response = self.client.models.generate_content(
        model=self.name, 
        contents=prompt
    )

    return response.text

  def generate(self, essay, rubric=None):

    if rubric is None:

      print("Generating without rubric")
      essay_prompt = essay.prompt
      print(essay_prompt)

      return self.geminiapi(essay.prompt)
    
    else:
      print("Generating with rubric")
      combined_prompt = rubric.text + essay.write_prompt 
      print(combined_prompt)
      
      return self.geminiapi(combined_prompt)

  def tune(self, essay, rubric):
      combined_prompt = essay.grade_prompt + rubric.text + essay.essay_text
      print(combined_prompt)
      
      return self.geminiapi(combined_prompt)
    

class Util:

  @staticmethod

  def texttojson(text, file_name):

    data = {"result": text}

    with open (file_name, 'w') as f:
      json.dump (data, f, indent=2)

    return file_name


  @staticmethod

  def jsontodoc(json):

    with open(json, "r",) as f:
      data = json.load(f)

    text = data["result"]

    clean_text = strip_markdown.strip_markdown(text)
    
    doc = Document()

    doc.add_paragraph(clean_text)

    doc.save(docx_name="output.docx")

    