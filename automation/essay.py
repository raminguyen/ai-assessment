from utils import load_prompts, json_to_docs 
from models import*
import json
import os
import time
import sys

prompt_1, prompt_2, base_direction= load_prompts()

class essay:
    def __init__(self):
        self.model = None

    def generate_essay(self, model, prompt_1=prompt_1):

        start = time.time()

        self.model = model

        print("Generating essay using model:", self.model)

        print("Using prompt:", prompt_1)

        #1. call model

        if model.startswith("gpt"):
            self.response_text = chatgpt(self.model, prompt_1)
            file_name = "chatgpt_generated_essay.json"
            self.pipeline_folder = "chatgpt_pipeline"

        elif model.startswith("gemini"):
            self.response_text = gemini(model, prompt_1)
            file_name = "gemini_generated_essay.json"
            self.pipeline_folder = "gemini_pipeline"

        elif model.startswith("claude"):
            self.response_text = claude(model, prompt_1)
            file_name = "claude_generated_essay.json"
            self.pipeline_folder = "claude_pipeline"

        else:
            print("model is not found")

        
        #2. SAVE OUTPUTS

        output_direction = os.path.join(base_direction, "outputs", self.pipeline_folder)

        os.makedirs(output_direction, exist_ok=True)

        output_json = os.path.join(output_direction, file_name)

        with open(output_json, "w") as f:

            json.dump({"essay": self.response_text}, f)


        json_to_docs(output_json, output_json.replace(".json", ".docx"))

        end = time.time()

        print(f"grade essay time {(end - start)/60} mins")

        print("Done.")

        return self.response_text
    
    def grade_essay(self, model, prompt_2=prompt_2):

        start= time.time()

        #1. Call model to grade essay

        self.model = model
        
        print("Grading essay using model", model)

        grade_prompt = prompt_2 + ' ' + self.response_text 

        print(grade_prompt)

        if model.startswith("gpt"):
            graded = chatgpt(self.model, grade_prompt)
            file_name = "chatgpt_graded_essay.json"


        elif model.startswith("gemini"):
            graded = gemini(model, grade_prompt)
            file_name = "gemini_graded_essay.json"

        elif model.startswith("claude"):
            graded = claude(model, grade_prompt)
            file_name = "claude_graded_essay.json"
        
        else:
            print("grade model is not found")

        #2. Save output

        output_direction = os.path.join(base_direction, "outputs", self.pipeline_folder)
        
        os.makedirs(output_direction, exist_ok=True)

        #3 Save Json

        output_json = os.path.join(output_direction, file_name)
        
        with open(output_json, "w") as f:

            json.dump({"graded_essay": graded}, f)

        #3. Convert json to docx 


        json_to_docs(output_json, output_json.replace(".json", ".docx"))

        end = time.time()

        print(f"grade essay time: {(end - start)/60} minutes")

        print("Done grading essay")

        return graded



    
        
              
    


        
