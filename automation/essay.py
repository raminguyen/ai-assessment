from models import*
import json
import os
import time

base_direction = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_direction, "assignmentprompt.json")

with open(file_path, "r") as f:
    data = json.load(f)
    prompt_1 = data["test_prompt"]
    print(prompt_1)

class essay:
    def __init__(self, model=str):
        self.model = model

    def generate_essay(self, prompt_1=prompt_1):

        start = time.time()

        print("Generating essay using model:", self.model)

        print("Using prompt:", prompt_1)

        #1. call model

        response_text = chatgpt(self.model, prompt_1)
        
        #2. save output

        with open("chatgpt_generated_essay.json", "w") as f:

            json.dump({"essay": response_text}, f)

        end = time.time()

        print(f"Time taken to generate essay: {end - start} seconds")

        print("Essay generated successfully.")

        

    
        
              
    


        
