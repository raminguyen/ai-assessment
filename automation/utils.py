import json
from docx import Document
import os
import strip_markdown



def load_prompts():
    base_direction = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_direction, "assignmentprompt.json")
    rubric_path = os.path.join(base_direction, "rubric.txt")

    with open(file_path, "r") as f:
        data = json.load(f)

    prompt_1_write = data["test_prompt"]

    prompt_2_grade = "starting grading using basic rubric. give me only 1 score and 5 words description"

    with open(rubric_path, "r") as f:
        rubric = f.read()

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

    print(clean_text)

    doc = Document()

    doc.add_paragraph(clean_text)

    doc.save(docx_name)


def run_pipeline(write_model, prompt_1, grade_model=None, description=str, rubric=None):

    
    from essay import essay
    
    pipeline = essay()

    pipeline.generate_essay(
        model=write_model,
        prompt_1=prompt_1,
        rubric=rubric
    )


    if isinstance(grade_model, (list, tuple)):
        for each_model in grade_model:
            pipeline.grade_essay(each_model)

    elif grade_model is None:
        print("No grading needed")
        
    else:
        pipeline.grade_essay(grade_model)    
    
    print(f"{description}: grading completed")


"""
from essay import essay

pipeline = essay()

pipeline.generate_essay(model=chatgpt, prompt_1=prompt_1_write, rubric = None)


pipeline.generate_essay(model=chatgpt, prompt_1=prompt_1_write, rubric = rubric)

sys.exit()

"""


