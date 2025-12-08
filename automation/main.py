from utils import*
import sys

# Define paramater 

assignment = "assignment_1"

all_models = [
    ("chatgpt", "gpt-4.1"),
    ("gemini", "gemini-3-pro-preview"),
    ("claude", "claude-sonnet-4-5"),
    ("grok", "grok-4-1-fast-reasoning")
]

prompt_1_write, prompt_2_grade, base_direction, rubric = load_prompts(assignment)

run_no_rubric = True
run_with_rubric = True

#
#
# 1. Pass argument
#
#

writing_models = all_models

# 2. Filter models: if argument is provided, use only this model.
if len(sys.argv) > 1: 

    which_model = sys.argv[1]

    filter_models = []

    for name, value in all_models:
        if name == which_model:
            filter_models.append((name,value))

    writing_models = filter_models
    

# 3. Filter experiments: rubric, norubric, both
if len(sys.argv) > 2:

    experiment_type = sys.argv[2]

    if experiment_type =="rubric":
        run_no_rubric = False
    elif experiment_type =="norubric":
        run_with_rubric = False

# 4. Get assignment from argument

if len(sys.argv) > 3:
    
    arg=sys.argv[3]
    if sys.argv[3].startswith("assignment"):
        assignment = sys.argv[3]
    elif arg.isdigit():
        assignment = f"assignment_{arg}"

# 5. Write essay, then other models grade it.
for model_name, model_value in writing_models:

    other_models = []

    for name, value in all_models:
        if name != model_name: 
            other_models.append(value)

    if run_no_rubric:
        print(model_name, "without rubric")
        print('Prompt preview', prompt_1_write)
        run_pipeline(
            write_model=model_value,
            prompt_1=prompt_1_write,
            grade_model=other_models,
            description=model_name + " write essay with no rubric",
            rubric=None,
            assignment=assignment
        )

    if run_with_rubric:
        print(model_name, "with rubric")
        print('Prompt preview', prompt_1_write)

        run_pipeline(
            write_model=model_value,
            prompt_1=prompt_1_write, 
            grade_model=other_models,
            description=model_name+ " tuned essays with rubrics",
            rubric=rubric,
        )

