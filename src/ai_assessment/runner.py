import argparse
import os
import json
from ai_assessment import Util, ModelChatGPT, ModelClaude, ModelGemini3ProPreview, ModelGrok
from ai_assessment.rubric.rubric import Rubric

class Runner:
    def main(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('assignment', choices=['a1', 'a2', 'a3'])
        parser.add_argument('model', choices=['chatgpt', 'gemini', 'claude', 'grok'])
        parser.add_argument('test', choices=['test0', 'test1', 'test2'])
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

        if args.tune:
            print(f"\nTuning essay for {args.assignment}_test_{{test_num}}_prompt...")
            print(f"Prompt: {essay.write_prompt[:100]}...")

            # Load rubric
            rubric_obj = Rubric(rubric_name)

            # Tune directly with the test prompt (no generation needed)
            data = model.tune(essay, rubric_obj)
            data['prompt'] = essay.write_prompt
            data['rubric'] = rubric_name
            data['folder'] = rubric_name

            filename = f"{args.assignment}_test{test_num}_tune_{args.model}.json"
        
        else:
                print(f"\nGenerating essay with {args.assignment}_test_{test_num}_prompt...")
                print(f"Prompt: {essay.write_prompt[:100]}...")
                data = model.generate(essay)

                filename = f"{args.assignment}_test{test_num}_{args.model}.json"


        # Save to test folder
        test_folder = os.path.join(args.test, 'data', rubric_name)
        os.makedirs(test_folder, exist_ok=True)

        filepath = os.path.join(test_folder, filename)

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        action = "Tuning" if args.tune else "Test"
        print(f"\n{action} {test_num} complete!")
        print(f"Saved to: {filepath}")


  