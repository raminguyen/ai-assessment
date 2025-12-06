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

    def generate_essay(self, model, prompt_1=prompt_1_write, rubric=None):

        start = time.time()

        self.model = model

        print("Generating essay using model:", self.model)

        if rubric is not None:
            prompt = prompt_1 + " " + rubric
            print(prompt)
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

        
        #2. SAVE JSON

        output_direction = os.path.join(base_direction, "outputs", self.pipeline_folder)

        os.makedirs(output_direction, exist_ok=True)

        output_json = os.path.join(output_direction, file_name)

        with open(output_json, "w") as f:

            json.dump({"essay": self.response_text}, f)

        #3: SAVE DOCS

        docs_direction = os.path.join(base_direction, "outputs", self.pipeline_folder, "docs")        

        os.makedirs(docs_direction, exist_ok=True)

        docx_path = os.path.join(docs_direction, file_name.replace(".json", ".docx"))

        json_to_docs(output_json, docx_path)

        end = time.time()

        print(f"generate essay time {(end - start)/60} mins")

        print("--------------------------------------------")

        print("Done.")

        return self.response_text
    

    """
    
    GRADE ESSAY
    
    """
    
    def grade_essay(self, model, prompt_2=prompt_2_grade):

        start= time.time()

    
        self.model = model
        
        print("Grading essay using model", model)

        grade_prompt = prompt_2 + ' ' + self.response_text 

        print(grade_prompt)

        if model.startswith("gpt"):
            graded = chatgpt(self.model, grade_prompt)
            file_name = "chatgpt_grade_tuned_essays.json" if self.used_rubric else "chatgpt_grade.json"

        elif model.startswith("gemini"):
            graded = gemini(model, grade_prompt)
            file_name = "gemini_grade_tuned_essay.json" if self.used_rubric else "gemini_grade_essay"

        elif model.startswith("claude"):
            graded = claude(model, grade_prompt)
            file_name = "claude_grade_tuned_essay.json" if self.used_rubric else "claude_grade_essay"

        elif model.startswith("grok"):
            graded = grok(model, grade_prompt)
            file_name = "groke_grade_tuned_essay.json" if self.used_rubric else "grok_grade_essay"
        
        else:
            print("grade model is not found")

        """ 
        
        SAVE OUTPUTS 
        
        """    

        
        #1: CREATE NEW FOLDER

        output_direction = os.path.join(base_direction, "outputs", self.pipeline_folder)
        
        os.makedirs(output_direction, exist_ok=True)

        # 2: SAVE JSON

        output_json = os.path.join(output_direction, file_name)
        
        with open(output_json, "w") as f:

            json.dump({"graded_essay": graded}, f)

        #3: SAVE DOCS

        docs_direction = os.path.join(base_direction, "outputs", self.pipeline_folder, "docs")        

        os.makedirs(docs_direction, exist_ok=True)

        docx_path = os.path.join(docs_direction, file_name.replace(".json", ".docx"))

        json_to_docs(output_json, docx_path)
        
        end = time.time()

        print(f"grade essay time: {(end - start)/60} minutes")

        print("Done grading essay, rami cool")

        print("--------------------------------------------")

        return graded



    
        
              
    


        
