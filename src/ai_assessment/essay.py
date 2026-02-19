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

        print(f"Loading prompts from: {file_path}")

        # Map assignment number to professor type
        professor_types = {
            1: "Psychology",
            2: "Economics",
            3: "Data Science"
        }

        self.write_prompt = data[f"assignment_{assignment_num}_prompt"]
        self.grade_prompt = data["grade_prompt"]
        self.reflection_prompt = data["reflection_prompt"]
        self.tuning_prompt = data["tuning_prompt"]

        # Replace the professor type placeholder
        professor_type = professor_types.get(assignment_num, "Psychology")
        self.grade_prompt = self.grade_prompt.replace("{PROFESSOR_TYPE}", professor_type)

        return self.write_prompt, self.grade_prompt

    def load_test_prompt(self, test_num=1, assignment_num=1):
        base_direction = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_direction, "prompt.json")

        with open(file_path, 'r') as f:
            data = json.load(f)

        print("Loading test prompts from: " + file_path)

        # Load prompt in format: a1_test_1_prompt, a2_test_2_prompt, etc.
        if test_num == 0:
           self.write_prompt = data["assignment_" + str(assignment_num) + "_p1"]
        else:
            prompt_key = "a" + str(assignment_num) + "_test_" + str(test_num) + "_prompt"
            self.write_prompt = data[prompt_key]

        self.grade_prompt = data["grade_prompt"]
        self.reflection_prompt = data["reflection_prompt"]

        # Use test-specific tuning prompt (tuning_prompt_0, tuning_prompt_1, tuning_prompt_2)
        tuning_prompt_key = "tuning_prompt_" + str(test_num)
        self.tuning_prompt = data.get(tuning_prompt_key, data["tuning_prompt_0"])

        # Map assignment number to professor type
        professor_types = {
            1: "Psychology",
            2: "Economics",
            3: "Real Estate"
        }
        professor_type = professor_types.get(assignment_num, "Psychology")
        self.grade_prompt = self.grade_prompt.replace("{PROFESSOR_TYPE}", professor_type)

        return self.write_prompt, self.grade_prompt

    def load_prompt_p(self, prompt_num=1, assignment_num=1):
        base_direction = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_direction, "prompt.json")

        with open(file_path, 'r') as f:
            data = json.load(f)

        print("Loading prompt p" + str(prompt_num) + " from: " + file_path)

        # Load prompt in format: assignment_1_p1, assignment_2_p2, etc.
        prompt_key = "assignment_" + str(assignment_num) + "_p" + str(prompt_num)

        if prompt_key not in data:
            prompt_key = prompt_key + "_generate"

        self.write_prompt = data[prompt_key]

        grade_key = "grade_prompt_p" + str(prompt_num)
        self.grade_prompt = data.get(grade_key, data["grade_prompt"])
        self.reflection_prompt = data["reflection_prompt"]

        # Use prompt-specific tuning (tuning_p1, tuning_p2)
        tuning_key = "tuning_p" + str(prompt_num)
        self.tuning_prompt = data.get(tuning_key, data["tuning_p1"])

        # Map assignment number to professor type
        professor_types = {
            1: "Psychology",
            2: "Economics",
            3: "Real Estate"
        }
        professor_type = professor_types.get(assignment_num, "Psychology")
        self.grade_prompt = self.grade_prompt.replace("{PROFESSOR_TYPE}", professor_type)

        return self.write_prompt, self.grade_prompt

    def load_prompt_p7(self, assignment_num=1, prompt_num=7):
        base_direction = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_direction, "prompt.json")

        with open(file_path, 'r') as f:
            data = json.load(f)

        print("Loading iterative prompt p" + str(prompt_num) + " from: " + file_path)

        context_key = "assignment_" + str(assignment_num) + "_p" + str(prompt_num) + "_context"
        generate_key = "assignment_" + str(assignment_num) + "_p" + str(prompt_num) + "_generate"
        self.context_prompt = data[context_key]
        self.generate_prompt = data[generate_key]
        self.write_prompt = self.context_prompt + "\n\n" + self.generate_prompt

        self.grade_prompt = data["grade_prompt"]
        self.reflection_prompt = data["reflection_prompt"]
        self.tuning_prompt = data.get("tuning_p1")

        professor_types = {
            1: "Psychology",
            2: "Economics",
            3: "Real Estate"
        }
        professor_type = professor_types.get(assignment_num, "Psychology")
        self.grade_prompt = self.grade_prompt.replace("{PROFESSOR_TYPE}", professor_type)

        return self.context_prompt, self.generate_prompt