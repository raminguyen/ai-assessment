import argparse
from datetime import datetime
from ai_assessment import Rubric, ModelChatGPT, ModelClaude, ModelGemini3ProPreview, ModelGrok, Util
import os 
def main():

    all_models = {
        "gemini": ModelGemini3ProPreview(),
        "chatgpt": ModelChatGPT(),
        "claude": ModelClaude(),
        "grok": ModelGrok()
    }

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
    score.add_argument('grader', choices=['chatgpt', 'gemini', 'claude', 'grok'], help="The model doing the grading")
    score.add_argument('rubric', type=str)
    score.add_argument('filename', help='Individual file to read')
    score.add_argument('assignment', type=int)
    
    args = parser.parse_args()

    def generate_cmd(args):
        model = all_models[args.model]

        if Util.check_data_exists(args.assignment, 'generate', args.model, rubric=None):
            print('Already exists, skipping: ' + args.model + ' generate assignment ' + str(args.assignment))
            return

        model = all_models[args.model]
        essay = Util.create_essay(args.assignment)

        data = model.generate(essay)
        
        Util.save_individual_file(data, args.assignment, 'generate', args.model, rubric=None)


    def tune_cmd(args):

        model = all_models[args.model]

        if Util.check_data_exists(args.assignment, 'tune', args.model, rubric=args.rubric):
            print('Already exists, skipping: ' + args.model + ' tune assignment ' + str(args.assignment))
            return

        #1. Set up model, essay, and rubric
        model = all_models[args.model]
        essay = Util.create_essay(args.assignment)
        rubric = Rubric(args.rubric)
        
        #2. Tune and save
        data = model.tune(essay, rubric)
        data['rubric'] = args.rubric
        
        Util.save_individual_file(data, args.assignment, 'tune', args.model, rubric=args.rubric)


    def score_cmd(args):
        grader_model = all_models[args.grader]

        essay_type = args.filename.split('_')[2]
        writer = args.filename.split('_')[3].replace('.json', '')
        
        # Load essay first to get writer_name
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
    
    #
    # Route to command
    #

    if args.command == 'generate':
        generate_cmd(args)
    elif args.command == 'tune':
        tune_cmd(args)
    elif args.command == 'score':
        score_cmd(args)
    elif args.command == 'exporttodocs':
        Util.export_all_to_docs()


if __name__ == "__main__":
    main()