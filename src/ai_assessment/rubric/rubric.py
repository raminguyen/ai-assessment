import os
import json

class Rubric:
    def __init__(self, rubric_type):
        base_direction = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_direction, "rubric.json")
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        self.text = data[rubric_type]