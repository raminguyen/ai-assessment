import argparse
import json
import os
from datetime import datetime
from ai_assessment import (
    Essay,
    Rubric,
    ModelChatGPT,
    ModelClaude,
    ModelGemini3ProPreview,
    ModelGrok
)


def save_to_file(filename, data):
    """Append data to JSON file"""
    all_data = {"operations": []}
    
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            all_data = json.load(f)
    
    all_data["operations"].append(data)
    
    with open(filename, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    print('Saved to: ' + filename)


def main():
    
    all_models = {
        "gemini": ModelGemini3ProPreview(),
        "chatgpt": ModelChatGPT(),
        "claude": ModelClaude(),
        "grok": ModelGrok()
    }

    def generate_cmd(args):
        model = all_models[args.model]
        essay = Essay('Essay_' + str(args.assignment))
        essay.load_prompt(args.assignment)
        
        result = model.generate(essay)
        
        data = {
            "model": args.model,
            "command": "generate",
            "result": result,
            "time_minutes": round(essay.time / 60, 2)
        }
        
        # Save individual file
        individual_file = args.model + '_essay.json'
        with open(individual_file, 'w') as f:
            json.dump(data, f, indent=2)
        print('Saved to: ' + individual_file)
        
        # Save to assignment file
        assignment_file = 'assignment_' + str(args.assignment) + '.json'
        save_to_file(assignment_file, data)

    def tune_cmd(args):
        model = all_models[args.model]
        essay = Essay('Essay_' + str(args.assignment))
        rubric = Rubric(args.rubric)
        essay.load_prompt(args.assignment)
        
        result = model.tune(essay, rubric)
        
        data = {
            "model": args.model,
            "command": "tune",
            "rubric": args.rubric,
            "result": result,
            "time_minutes": round(essay.time / 60, 2)
        }
        
        # Save individual file
        individual_file = args.model + '_essay_tuned.json'
        with open(individual_file, 'w') as f:
            json.dump(data, f, indent=2)
        print('Saved to: ' + individual_file)
        
        # Save to assignment file
        assignment_file = 'assignment_' + str(args.assignment) + '.json'
        save_to_file(assignment_file, data)

    def score_cmd(args):
        model = all_models[args.model]
        
        with open(args.essay_file, 'r') as f:
            essay_data = json.load(f)
        
        if "operations" in essay_data:
            essay_text = essay_data["operations"][-1]["result"]
        else:
            essay_text = essay_data["result"]
        
        essay = Essay('Essay_' + str(args.assignment))
        rubric = Rubric(args.rubric)
        essay.load_prompt(args.assignment)
        essay.essay_text = essay_text
        
        result, elapsed = model.grade(essay, rubric)
        
        data = {
            "model": args.model,
            "command": "score",
            "rubric": args.rubric,
            "source": args.essay_file,
            "result": result,
            "time_minutes": round(elapsed / 60, 2)
        }
        
        # Save individual file
        individual_file = args.model + '_grade.json'
        with open(individual_file, 'w') as f:
            json.dump(data, f, indent=2)
        print('Saved to: ' + individual_file)
        
        # Save to assignment file
        assignment_file = 'assignment_' + str(args.assignment) + '.json'
        save_to_file(assignment_file, data)

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    
    gen = subparsers.add_parser('generate')
    gen.add_argument('model', choices=['chatgpt', 'gemini', 'claude', 'grok'])
    gen.add_argument('assignment', type=int)
    
    tune = subparsers.add_parser('tune')
    tune.add_argument('model', choices=['chatgpt', 'gemini', 'claude', 'grok'])
    tune.add_argument('rubric', type=str)
    tune.add_argument('assignment', type=int)
    
    score = subparsers.add_parser('score')
    score.add_argument('model', choices=['chatgpt', 'gemini', 'claude', 'grok'])
    score.add_argument('rubric', type=str)
    score.add_argument('essay_file', type=str)
    score.add_argument('assignment', type=int)
    
    args = parser.parse_args()
    
    if args.command == 'generate':
        generate_cmd(args)
    elif args.command == 'tune':
        tune_cmd(args)
    elif args.command == 'score':
        score_cmd(args)


if __name__ == "__main__":
    main()