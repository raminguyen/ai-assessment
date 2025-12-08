from utils import*
import sys

all_models = [
    ("chatgpt", "gpt-4.1"),
    ("gemini", "gemini-3-pro-preview"),
    ("claude", "claude-sonnet-4-5"),
    ("grok", "grok-4-1-fast-reasoning")
]

""" 

Pass argument

"""

writing_models = all_models

if len(sys.argv) > 1: 
    which_model = sys.argv[1]


    filter_models = []

    for name, value in all_models:
        if name == which_model:
            filter_models.append((name,value))

    writing_models = filter_models
    
run_no_rubric = True
run_with_rubric = True

if len(sys.argv) > 2:
    experiment_type = sys.argv[2]

    if experiment_type =="rubric":
        run_no_rubric = False
    elif experiment_type =="norubric":
        run_with_rubric = False


assignment = "assignment_1"

if len(sys.argv) > 3:
    
    arg=sys.argv[3]

    if sys.argv[3].startswith("assignment"):
        assignment = sys.argv[3]
    elif arg.isdigit():
        assignment = f"assignment_{arg}"

prompt_1_write, prompt_2_grade, base_direction, rubric = load_prompts(assignment)


for model_name, model_value in writing_models:

    other_models = []

    for name, value in all_models:
        if name != model_name: 
            other_models.append(value)

    if run_no_rubric:
        print(f"\n{model_name} (without rubric)")
        print(f"Prompt preview: {prompt_1_write[:100]}...")
        run_pipeline(
            write_model=model_value,
            prompt_1=prompt_1_write,
            grade_model=other_models,
            description=model_name + " write essay with no rubric",
            rubric=None,
            assignment=assignment
        )

    if run_with_rubric:
        print(f"\n{model_name} (with rubric)")

        run_pipeline(
            write_model=model_value,
            prompt_1=prompt_1_write, 
            grade_model=other_models,
            description=model_name+ " tuned essays with rubrics",
            rubric=rubric,
        )

