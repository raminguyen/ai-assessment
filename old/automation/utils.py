import json
from docx import Document
import os
import strip_markdown
import sys

def load_prompts(assignment="assignment_1"):

    prompt_key = f"{assignment}_prompt"
    
    base_direction = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_direction, "..", "prompts", "prompt.json")

    with open(file_path, "r") as f:
        data = json.load(f)

    prompt_1_write = data[prompt_key]
    prompt_2_grade = data["grade_prompt"]
    rubric = data["critical_thinking"]
   
    return prompt_1_write, prompt_2_grade, base_direction, rubric

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

    doc = Document()

    doc.add_paragraph(clean_text)

    doc.save(docx_name)


def run_pipeline(write_model, prompt_1, grade_model=None, description=str, rubric=None, assignment="assignment_1"):

    
    from essay import Writer, Grader
    
    writer = Writer()
    grader = Grader()

    writer.write(
        model=write_model,
        prompt_1=prompt_1,
        rubric=rubric,
        assignment=assignment
    )


    if isinstance(grade_model, (list, tuple)):

        for each_model in grade_model:
            grader.grade(
                model = each_model,
                essay_text=writer.response_text,
                used_rubric = writer.used_rubric,
                pipeline_folder=writer.pipeline_folder)
    

    elif grade_model is None:
        print("No grading needed")

    else:
        # Grade with single model
        grader = Grader()

        grader.grade(
            model=grade_model,
            essay_text=writer.response_text,
            used_rubric=writer.used_rubric,
            pipeline_folder=writer.pipeline_folder,
            assignment=assignment
        )  
    
    print(f"{description}: grading completed")



