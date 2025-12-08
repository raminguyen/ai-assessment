from utils import*
from models import*
import json
import os
import time

#load prompt
prompt_1_write, prompt_2_grade, base_direction, rubric = load_prompts()

class essay:
    def __init__(self):
        self.prompt_1_write = prompt_1_write
        self.prompt_2_grade = prompt_2_grade
        self.rubric = rubric
        
#
#
# 1. Write an essay
#
#

class generate_essay(essay):

    def __init__(self):
        super().__init__()


    def write(self, model, prompt_1=None, rubric=None, assignment="assignment_1"):

        ''' auto write essays '''

        self.model = model
        self.assignment = assignment

        start = time.time()

        print("Writing model is:", self.model)

        #1a. Combine rubric with prompt if provided

        if rubric is not None:
            prompt = rubric + " " + prompt_1
            print(f"combined prompt {prompt}")
            self.used_rubric = True
            
        else:
            prompt = prompt_1
            self.used_rubric = False

        #1b. CALL MODEL
        
        if model.startswith("gpt"):
            self.response_text = chatgpt(self.model, prompt)
            self.pipeline_folder = "chatgpt_pipeline"
            model_name = "chatgpt"


        elif model.startswith("gemini"):
            self.response_text = gemini(model, prompt)
            self.pipeline_folder = "gemini_pipeline"
            model_name = "gemini"

        elif model.startswith("claude"):
            self.response_text = claude(model, prompt)
            self.pipeline_folder = "claude_pipeline"
            model_name = "claude"

        elif model.startswith("grok"):
            self.response_text = grok(model, prompt)
            self.pipeline_folder = "grok_pipeline"
            model_name = "grok"

        else:
            print("model is not found")

        if self.used_rubric:
            file_name = f"{model_name}_write_tuned_essay"

        else:
            file_name = f"{model_name}_write_essay.json"

        if self.used_rubric:
            essay_folder = "tuned_essays" #with rubric
        else:
            essay_folder = "essays" #without rubric
        
 
        #1c. Save JSON
        output_direction = os.path.join(base_direction, "outputs", self.pipeline_folder, self.assignment, essay_folder)
        os.makedirs(output_direction, exist_ok=True)
        output_json = os.path.join(output_direction, file_name)

        with open(output_json, "w") as f:
            json.dump({"essay": self.response_text}, f)

        #1d: SAVE DOCS

        docs_direction = os.path.join(base_direction, "outputs", self.pipeline_folder, self.assignment, essay_folder, "docs")        
        os.makedirs(docs_direction, exist_ok=True)
        docx_path = os.path.join(docs_direction, file_name.replace(".json", ".docx"))

        json_to_docs(output_json, docx_path)
        end = time.time()

        print('Writing done and time', (end - start)/60, 'mins')

        return self.response_text
    

#
#
# 2. Grade an essay
#
#


class grade_essay(essay):
    
    ''' auto grade essays '''

    def __init__(self):
        super().__init__()

    def grade(self, model, essay_text, used_rubric, pipeline_folder, assignment="assignment_1"):

        self.response_text = essay_text
        self.used_rubric = used_rubric
        self.pipeline_folder = pipeline_folder
        self.assignment = assignment

        #2a. Call models

        start= time.time()

        self.model = model
        
        print("Grading model", model)

        grade_prompt = prompt_2_grade + ' ' + essay_text

        if model.startswith("gpt"):
            graded = chatgpt(self.model, grade_prompt)
            model_name = "chatgpt"

        elif model.startswith("gemini"):
            graded = gemini(model, grade_prompt)
            model_name = "gemini"
        
        elif model.startswith("claude"):
            graded = claude(model, grade_prompt)
            model_name = "claude"
    
        elif model.startswith("grok"):
            graded = grok(model, grade_prompt)
            model_name = "claude"

        else:
            print("grade model is not found")

        if self.used_rubric:
            file_name = f"{model_name}_graded_tuned_essay"

        else:
            file_name = f"{model_name}_grade_essay.json"

        #2b. SAVE OUTPUTS 

        if self.used_rubric:
            essay_folder = "tuned_essays" #with rubric

        else:
            essay_folder = "essays" #without rubric
        
        #2c: CREATE NEW FOLDER

        output_direction = os.path.join(base_direction, "outputs", self.pipeline_folder, self.assignment, essay_folder)
        
        os.makedirs(output_direction, exist_ok=True)

        # 2d: SAVE JSON

        output_json = os.path.join(output_direction, file_name)
        
        with open(output_json, "w") as f:

            json.dump({"graded_essay": graded}, f)

        #2e: SAVE DOCS

        docs_direction = os.path.join(base_direction, "outputs", self.pipeline_folder, self.assignment, essay_folder, "docs")        

        os.makedirs(docs_direction, exist_ok=True)

        docx_path = os.path.join(docs_direction, file_name.replace(".json", ".docx"))

        json_to_docs(output_json, docx_path)
        
        end = time.time()

        print('Writing done and time', (end - start)/60, 'mins')

        return graded



    
        
              
    


        
