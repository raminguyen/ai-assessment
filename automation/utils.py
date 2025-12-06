import json
from docx import Document
import os
import strip_markdown

def load_prompts():
    base_direction = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_direction, "assignmentprompt.json")

    with open(file_path, "r") as f:
        data = json.load(f)

    prompt_1 = data["test_prompt"]

    prompt_2 = "starting grading using basic rubric. give me only 1 score and 5 words description"

    return prompt_1, prompt_2, base_direction

def json_to_docs(json_name, docx_name):
    with open(json_name, "r") as f:
        data = json.load(f)

    if "essay" in data:
        text = data["essay"]
    elif "graded_essay" in data:
        text = data['graded_essay']
    else:
        print("error here: Rami: no json file.")

    clean_text = strip_markdown.strip_markdown(text)
    print(clean_text)

    doc = Document()

    doc.add_paragraph(clean_text)

    doc.save(docx_name)


def run_pipeline(write_model, grade_model, description=str):
    
    from essay import essay
    
    pipeline = essay()
    
    pipeline.generate_essay(write_model)
    print(f"{description}: essay completed")
    
    pipeline.grade_essay(grade_model)
    print(f"{description}: grading completed")




