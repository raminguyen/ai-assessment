import time
from datetime import datetime
from ai_assessment import Rubric, ModelChatGPT, ModelClaude, ModelGemini3ProPreview, ModelGrok, Util
import argparse

class Model:
    def __init__(self, model_name):
        self.name = model_name
        self.client = None
    
    def generate(self, essay):

        print("Generating an essay")
        start = time.time()
        result = self.api_call(essay.write_prompt)
        
        essay.essay_text = result
        essay.status = 1
        essay.time = time.time() - start
        print(f"Done in {essay.time/60:.2f} mins")
        time.sleep(5)
        
        # Create a JSON data
        data = {
            "command": "generate",
            "model": self.name,
            "essay_name": essay.name,
            "result": result,
            "time_minutes": round(essay.time / 60, 2),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return data
    
    def tune(self, essay, rubric):

        print("Tuning with rubric")
        start = time.time()
        result = self.api_call(rubric.text + essay.write_prompt)
        
        essay.essay_text = result
        essay.status = 2
        essay.time = time.time() - start
        print(f"Done in {essay.time/60:.2f} mins")

        time.sleep(5)
        
        data = {
            "command": "tune",
            "model": self.name,
            "essay_name": essay.name,
            "result": result,
            "time_minutes": round(essay.time / 60, 2),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return data
    
    def score(self, essay, rubric, writer=None, essay_type=None):

        print("Grading essay")
        start = time.time()
        result = self.api_call(essay.grade_prompt + rubric.text + essay.essay_text)
        
        essay.grade_result = result
        essay.status = 3
        elapsed = time.time() - start
        print(f"Done in {elapsed/60:.2f} mins")
        time.sleep(5)
        
        # Create and return data
        data = {
            "command": "score",
            "grader": self.name,
            "writer": writer,
            "essay_type": essay_type,
            "essay_name": essay.name,
            "result": result,
            "time_minutes": round(elapsed / 60, 2),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
        return data
    
class Runner:
    def __init__(self):
        self.all_models = {
            "gemini": ModelGemini3ProPreview(),
            "chatgpt": ModelChatGPT(),
            "claude": ModelClaude(),
            "grok": ModelGrok()
        }
    
    def generate(self, args):
        model = self.all_models[args.model]
        rubric = args.folder

        if Util.check_data_exists(args.assignment, 'generate', args.model, rubric=rubric):
            print('Already exists, skipping: ' + args.model + ' generate assignment ' + str(args.assignment))
            return

        essay = Util.create_essay(args.assignment)
        data = model.generate(essay)
        Util.save_individual_file(data, args.assignment, 'generate', args.model, rubric=rubric)

    def tune(self, args):
        model = self.all_models[args.model]

        if Util.check_data_exists(args.assignment, 'tune', args.model, rubric=args.rubric):
            print('Already exists, skipping: ' + args.model + ' tune assignment ' + str(args.assignment))
            return

        essay = Util.create_essay(args.assignment)
        rubric = Rubric(args.rubric)
        
        data = model.tune(essay, rubric)
        data['rubric'] = args.rubric
        Util.save_individual_file(data, args.assignment, 'tune', args.model, rubric=args.rubric)

    def score(self, args):
        grader_model = self.all_models[args.grader]
        
        essay_text, writer_name, essay_type = Util.load_essay_from_data(args.filename, rubric=args.rubric)

        if Util.check_data_exists(args.assignment, 'score', args.grader, essay_type=essay_type, writer=writer_name, rubric=args.rubric):
            print('Already exists, skipping: ' + args.grader + ' scoring ' + essay_type + ' assignment ' + str(args.assignment))
            return
        
        essay = Util.create_essay(args.assignment)
        rubric = Rubric(args.rubric)
        essay.essay_text = essay_text

        data = grader_model.score(essay, rubric, writer=writer_name, essay_type=essay_type)
        data['rubric'] = args.rubric
        data['scored_essay_text'] = essay_text
        data['essay_type'] = essay_type

        Util.save_individual_file(data, args.assignment, 'score', args.grader, essay_type=essay_type, rubric=args.rubric, writer=writer_name)

    def run(self, args):
        """Route to command"""
        if args.command == 'generate':
            self.generate(args)
        elif args.command == 'tune':
            self.tune(args)
        elif args.command == 'score':
            self.score(args)