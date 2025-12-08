from utils import load_prompts, json_to_docs 
from models import*
import json
import os
import time
import sys

prompt_1_write, prompt_2_grade, base_direction, rubric = load_prompts()

class essay:
    def __init__(self):
        self.prompt_1_write = prompt_1_write
        self.prompt_2_grade = prompt_2_grade
        self.rubric = rubric
    """
    
    WRITE ESSAY
    
    """

class generate_essay(essay):

    def __init__(self):
        super().__init__()


    def write(self, model, prompt_1=None, rubric=None, assignment="assignment_1"):

        start = time.time()

        self.model = model
        self.assignment = assignment

        print("Writing model is:", self.model)

        if rubric is not None:
            prompt = rubric + " " + prompt_1
            print(f"combined prompt {prompt}")
            self.used_rubric = True
            
        else:
            prompt = prompt_1
            self.used_rubric = False

    
        #1. CALL MODEL

        if model.startswith("gpt"):
            self.response_text = chatgpt(self.model, prompt)
            file_name = "chatgpt_tuned_essay.json" if self.used_rubric else "chatgpt_write_essay.json"
            self.pipeline_folder = "chatgpt_pipeline"


        elif model.startswith("gemini"):
            self.response_text = gemini(model, prompt)
            file_name = "gemini_tuned_essay.json" if self.used_rubric else "gemini_write_essay.json"
            self.pipeline_folder = "gemini_pipeline"

        elif model.startswith("claude"):
            self.response_text = claude(model, prompt)
            file_name = "claude_tuned_essa.json" if self.used_rubric else "claude_write_essay.json"
            self.pipeline_folder = "claude_pipeline"

        elif model.startswith("grok"):
            self.response_text = grok(model, prompt)
            file_name = "grok_tuned_essay.json" if self.used_rubric else "grok_write_essay.json"
            self.pipeline_folder = "grok_pipeline"

        else:
            print("model is not found")

        if self.used_rubric:
            essay_folder = "tuned_essays" #with rubric
        else:
            essay_folder = "essays" #without rubric
        
        #2. SAVE JSON

        output_direction = os.path.join(base_direction, "outputs", self.pipeline_folder, self.assignment, essay_folder)

        os.makedirs(output_direction, exist_ok=True)

        output_json = os.path.join(output_direction, file_name)

        with open(output_json, "w") as f:

            json.dump({"essay": self.response_text}, f)

        #3: SAVE DOCS

        docs_direction = os.path.join(base_direction, "outputs", self.pipeline_folder, self.assignment, essay_folder, "docs")        

        os.makedirs(docs_direction, exist_ok=True)

        docx_path = os.path.join(docs_direction, file_name.replace(".json", ".docx"))

        json_to_docs(output_json, docx_path)

        end = time.time()

        print(f"writing done and time  ({(end - start)/60:.1f} min)")

        return self.response_text
    

    

    """
    
    GRADE ESSAY
    
    """
    
class grade_essay(essay):

    def __init__(self):
        super().__init__()

    def grade(self, model, essay_text, used_rubric, pipeline_folder, assignment="assignment_1"):

        self.response_text = essay_text
        self.used_rubric = used_rubric
        self.pipeline_folder = pipeline_folder
        self.assignment = assignment

        start= time.time()

        self.model = model
        
        print("Grading model", model)

        grade_prompt = prompt_2_grade + ' ' + essay_text

        if model.startswith("gpt"):
            graded = chatgpt(self.model, grade_prompt)
            file_name = "chatgpt_grade_tuned_essays.json" if self.used_rubric else "chatgpt_grade.json"

        elif model.startswith("gemini"):
            graded = gemini(model, grade_prompt)
            file_name = "gemini_grade_tuned_essay.json" if self.used_rubric else "gemini_grade_essay.json"

        elif model.startswith("claude"):
            graded = claude(model, grade_prompt)
            file_name = "claude_grade_tuned_essay.json" if self.used_rubric else "claude_grade_essay.json"

        elif model.startswith("grok"):
            graded = grok(model, grade_prompt)
            file_name = "groke_grade_tuned_essay.json" if self.used_rubric else "grok_grade_essay.json"
        
        else:
            print("grade model is not found")

        """ 
        
        SAVE OUTPUTS 
        
        """    

        if self.used_rubric:
            essay_folder = "tuned_essays" #with rubric
        else:
            essay_folder = "essays" #without rubric
        
        #1: CREATE NEW FOLDER

        output_direction = os.path.join(base_direction, "outputs", self.pipeline_folder, self.assignment, essay_folder)
        
        os.makedirs(output_direction, exist_ok=True)

        # 2: SAVE JSON

        output_json = os.path.join(output_direction, file_name)
        
        with open(output_json, "w") as f:

            json.dump({"graded_essay": graded}, f)

        #3: SAVE DOCS

        docs_direction = os.path.join(base_direction, "outputs", self.pipeline_folder, self.assignment, essay_folder, "docs")        

        os.makedirs(docs_direction, exist_ok=True)

        docx_path = os.path.join(docs_direction, file_name.replace(".json", ".docx"))

        json_to_docs(output_json, docx_path)
        
        end = time.time()

        print(f"grade done and essay time: ({(end - start)/60:.1f} min)")

        return graded



    
        
              
    


        
