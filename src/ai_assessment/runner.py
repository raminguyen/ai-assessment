import argparse
import os
import json
from ai_assessment import Util, ModelChatGPT, ModelClaude, ModelGemini3ProPreview, ModelGrok
from ai_assessment.rubric.rubric import Rubric

class Runner:

    def __init__(self):
        self.all_models = {
            "gemini": ModelGemini3ProPreview(),
            "chatgpt": ModelChatGPT(),
            "claude": ModelClaude(),
            "grok": ModelGrok()
        }

    def generate(self, model_name, assignment, rubric_name, prompt_num=1):
        model = self.all_models[model_name]

        essay = Util.create_essay(assignment, rubric_folder=rubric_name)
        essay.load_prompt_p(prompt_num, assignment)

        # Build filename with prompt suffix
        filename = Util.build_filename(assignment, 'generate', model_name, prompt_num=prompt_num)
        folder = os.path.join('..', 'data', rubric_name)
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)

        # Check if file exists
        if os.path.exists(filepath):
            print("Skipping: " + filename + " already exists")
            return

        print("Generating essay for assignment " + str(assignment) + " with prompt " + str(prompt_num))

        data = model.generate(essay, rubric_name)
        
        data['prompt_num'] = prompt_num

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        print("Saved: " + filepath)

    def tune(self, model_name, assignment, rubric_name, prompt_num=1):
        model = self.all_models[model_name]

        essay = Util.create_essay(assignment, rubric_folder=rubric_name)
        essay.load_prompt_p(prompt_num, assignment)

        rubric_obj = Rubric(rubric_name)

        # Build filename with prompt suffix
        filename = Util.build_filename(assignment, 'tune', model_name, prompt_num=prompt_num)
        folder = os.path.join('..', 'data', rubric_name)
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)

        # Check if file exists
        if os.path.exists(filepath):
            print("Skipping: " + filename + " already exists")
            return

        print("Tuning essay for assignment " + str(assignment) + " with prompt " + str(prompt_num))

        data = model.tune(essay, rubric_obj)
        data['prompt_num'] = prompt_num
        data['rubric'] = rubric_name

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        print("Saved: " + filepath)

    def score(self, grader_name, rubric_name, filename, assignment, prompt_num=1):
        grader = self.all_models[grader_name]

        essay = Util.create_essay(assignment, rubric_folder=rubric_name)
        essay.load_prompt_p(prompt_num, assignment)

        # Load essay from file
        essay_text, writer_model, essay_type = Util.load_essay_from_data(filename, rubric_name)
        essay.essay_text = essay_text

        rubric_obj = Rubric(rubric_name)

        # Get writer short name from filename
        name_map = {
            "gpt-5.2-2025-12-11": "chatgpt",
            "grok-4-1-fast-reasoning": "grok",
            "gemini-3-pro-preview": "gemini",
            "claude-sonnet-4-5-20250929": "claude"
        }
        short_writer = name_map.get(writer_model, writer_model)

        # Build score filename with prompt suffix
        score_filename = Util.build_filename(assignment, 'score', grader_name, essay_type, short_writer, prompt_num)
        folder = os.path.join('..', 'data', rubric_name)
        filepath = os.path.join(folder, score_filename)

        # Check if file exists
        if os.path.exists(filepath):
            print("Skipping: " + score_filename + " already exists")
            return

        print("Scoring " + filename + " with " + grader_name)

        data = grader.score(essay, rubric_obj, writer_model, essay_type)
        data['prompt_num'] = prompt_num

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        print("Saved: " + filepath)

    def reflect(self, model_name, assignment, rubric_name, prompt_num=1):
        model = self.all_models[model_name]

        essay = Util.create_essay(assignment, rubric_folder=rubric_name)
        essay.load_prompt_p(prompt_num, assignment)

        rubric_obj = Rubric(rubric_name)

        # Load original generated essay
        gen_filename = Util.build_filename(assignment, 'generate', model_name, prompt_num=prompt_num)
        original_essay, _, _ = Util.load_essay_from_data(gen_filename, rubric_name)

        # Load tuned essay
        tune_filename = Util.build_filename(assignment, 'tune', model_name, prompt_num=prompt_num)
        tuned_essay, _, _ = Util.load_essay_from_data(tune_filename, rubric_name)

        # Build reflection filename
        filename = Util.build_filename(assignment, 'reflection', model_name, prompt_num=prompt_num)
        folder = os.path.join('..', 'data', rubric_name)
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)

        # Check if file exists
        if os.path.exists(filepath):
            print("Skipping: " + filename + " already exists")
            return

        print("Generating reflection for assignment " + str(assignment) + " with prompt " + str(prompt_num))

        data = model.reflect(essay, original_essay, tuned_essay, rubric_obj)
        data['prompt_num'] = prompt_num

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        print("Saved: " + filepath)

    def main(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('assignment', choices=['a1', 'a2', 'a3'])
        parser.add_argument('model', choices=['chatgpt', 'gemini', 'claude', 'grok'])
        parser.add_argument('test', choices=['test0', 'test1', 'test2', 'test3', 'test4', 'test5', 'test6'])
        parser.add_argument('--folder', type=str, default='critical_thinking')
        parser.add_argument('--tune', action='store_true', help='Run tuning instead of generation')

        args = parser.parse_args()

        # Extract assignment number (a1 -> 1, a2 -> 2, a3 -> 3)
        assignment_num = int(args.assignment.replace('a', ''))

        # Extract test number from test argument (test1 -> 1, test2 -> 2)
        test_num = int(args.test.replace('test', ''))

        all_models = {
            "gemini": ModelGemini3ProPreview(),
            "chatgpt": ModelChatGPT(),
            "claude": ModelClaude(),
            "grok": ModelGrok()
        }

        model = all_models[args.model]
        rubric_name = args.folder

        essay = Util.create_essay(assignment_num, rubric_folder=rubric_name)
        essay.load_test_prompt(test_num, assignment_num)

        # Determine filename and filepath first
        if args.tune:
            filename = f"{args.assignment}_test{test_num}_tune_{args.model}.json"
        else:
            filename = f"{args.assignment}_test{test_num}_{args.model}.json"

        # Save to test folder
        test_folder = os.path.join(args.test, 'data', rubric_name)
        os.makedirs(test_folder, exist_ok=True)
        filepath = os.path.join(test_folder, filename)

        # Check if file already exists
        if os.path.exists(filepath):
            print(f"\nSkipping: {filename} already exists")
            print(f"Location: {filepath}")
            return

        # Generate or tune
        if args.tune:
            print(f"\nTuning essay for {args.assignment}_test_{test_num}_prompt...")
            print(f"Prompt: {essay.write_prompt[:100]}...")

            # Load rubric
            rubric_obj = Rubric(rubric_name)

            # Tune directly with the test prompt (no generation needed)
            data = model.tune(essay, rubric_obj)
            data['prompt'] = essay.write_prompt
            data['rubric'] = rubric_name
            data['folder'] = rubric_name

        else:
            print(f"\nGenerating essay with {args.assignment}_test_{test_num}_prompt...")
            print(f"Prompt: {essay.write_prompt[:100]}...")
            data = model.generate(essay)

        # Save the file
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        action = "Tuning" if args.tune else "Test"
        print(f"\n✅ {action} {test_num} complete!")
        print(f"Saved to: {filepath}")


  