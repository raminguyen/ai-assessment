from test import Rubric, Essay, Model, ModelGemini3ProPreview, ModelChatGPT, ModelClaude, ModelGrok
from test import Util
import os
import sys
import argparse

# Parse arguments

parser = argparse.ArgumentParser()
parser.add_argument("writer", choices =["gemini", "chatgpt", "claude", "grok"], help="Model to write essay")
parser.add_argument('rubric', type=str, help='Rubric type (norubric/rubric)')
parser.add_argument('assignment', type=int, help='Assignment number (1, 2, 3)')

args = parser.parse_args()

# Set up models
gemini = ModelGemini3ProPreview()
chatgpt = ModelChatGPT()
claude = ModelClaude()
grok = ModelGrok()

# Model mapping
all_models = {
    "gemini": gemini,
    "chatgpt": chatgpt,
    "claude": claude,
    'grok': grok
}

writer_model = all_models[args.writer]

graders = {}

for name, model in all_models.items():
    if name != args.writer:
        graders[name] = model


# Set up essay and rubric
essay = Essay(f"Essay_{args.assignment}")
rubric = Rubric("critical_thinking")
essay.load_prompt(args.assignment) #return write_prompt, and grade_prompt

base_folder = f"assignment_{args.assignment}/{args.writer}"


def grade_all(essay, rubric, graders, writer_model, essay_file, assignment):
    grade_files = []
    for name in graders:
        graded = graders[name].grade(essay, rubric)
        grade_file = f"{name}_grade_essay{assignment}.json"
        Util.texttojson(graded, grade_file, essay, rubric, writer_model=writer_model, grader_model=graders[name], source_file=essay_file)
        grade_files.append(grade_file)
    return grade_files


#
# Without Rubric
#

if args.rubric == "norubric":
    Util.OUTPUT_FOLDER = f"{base_folder}/norubric"
    
    generated = writer_model.generate(essay)
    essay_file = f"{args.writer}_generate_essay{args.assignment}.json"
    Util.texttojson(generated, essay_file, essay, writer_model=writer_model)
    
    essay.essay_text = Util.load_essay(essay_file)
    grade_files = grade_all(essay, rubric, graders, writer_model, essay_file, args.assignment)
    
    Util.batch_jsontodoc([essay_file] + grade_files)

#
# With Rubric
#

else:
    Util.OUTPUT_FOLDER = f"{base_folder}/withrubric"
    
    tuned = writer_model.tune(essay, rubric)
    essay_file = f"{args.writer}_tuned_essay{args.assignment}.json"
    Util.texttojson(tuned, essay_file, essay, rubric, writer_model=writer_model)
    
    essay.essay_text = Util.load_essay(essay_file)
    grade_files = grade_all(essay, rubric, graders, writer_model, essay_file, args.assignment)
    
    Util.batch_jsontodoc([essay_file] + grade_files)

print("Rami is done.")