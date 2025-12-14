import os
import json


class Essay:
    def __init__(self, name):
        self.status = 0
        self.name = name
        self.prompt = None
        self.model = None
        self.essay_text = None
    
    def load_prompt(self, assignment_num=1):
        base_direction = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_direction, "prompt.json")
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        self.write_prompt = data[f"assignment_{assignment_num}_prompt"]
        self.grade_prompt = data["grade_prompt"]
        
        return self.write_prompt, self.grade_prompt