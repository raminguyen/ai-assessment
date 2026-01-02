import os
import json


class Essay:
    def __init__(self, name, rubric_folder):
        self.status = 0
        self.name = name
        self.prompt = None
        self.model = None
        self.essay_text = None
        self.rubric_folder = rubric_folder
    
    def load_prompt(self, assignment_num=1):
        base_direction = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_direction, "prompt.json")

        with open(file_path, 'r') as f:
            data = json.load(f)

        # Map assignment number to professor type
        professor_types = {
            1: "Psychology",
            2: "Economics",
            3: "Business Analytics"
        }

        self.write_prompt = data[f"assignment_{assignment_num}_prompt"]
        self.grade_prompt = data["grade_prompt"]
        self.reflection_prompt = data["reflection_prompt"]
        self.tuning_prompt = data["tuning_prompt"]

        # Replace the professor type placeholder
        professor_type = professor_types.get(assignment_num, "Psychology")
        self.grade_prompt = self.grade_prompt.replace("{PROFESSOR_TYPE}", professor_type)

        return self.write_prompt, self.grade_prompt