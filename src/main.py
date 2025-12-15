import argparse
from datetime import datetime
from ai_assessment import Rubric, ModelChatGPT, ModelClaude, ModelGemini3ProPreview, ModelGrok, Util

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
    score.add_argument('writer', choices=['chatgpt', 'gemini', 'claude', 'grok'], help="The model that wrote the essay")

    score.add_argument('essay_type', choices=['generate', 'tune'], help='Which essay to score')
    score.add_argument('rubric', type=str)
    score.add_argument('assignment', type=int)
    
    args = parser.parse_args()

    def generate_cmd(args):

        model = all_models[args.model]

        if Util.check_data_exists(args.assignment, 'generate', model.name):
            print('Already exists, skipping: ' + args.model + ' generate assignment ' + str(args.assignment))
            return

        #1.Set up model and essay
        model = all_models[args.model]
        essay = Util.create_essay(args.assignment)

        #2.Generate and save
        data = model.generate(essay)
        Util.save_data(data, args.assignment)

    def tune_cmd(args):

        model = all_models[args.model]

        if Util.check_data_exists(args.assignment, 'tune', model.name, rubric=args.rubric):
            print('Already exists, skipping: ' + args.model + ' tune assignment ' + str(args.assignment))
            return

        #1. Set up model, essay, and rubric
        model = all_models[args.model]
        essay = Util.create_essay(args.assignment)
        rubric = Rubric(args.rubric)
        
        #2. Tune and save
        data = model.tune(essay, rubric)
        data['rubric'] = args.rubric
        Util.save_data(data, args.assignment)

    def score_cmd(args):

        grader_model = all_models[args.grader]
        writer_target = args.writer

        if Util.check_data_exists(args.assignment, 'score', grader_model.name, essay_type=args.essay_type, writer=args.writer, rubric=args.rubric):
            print('Already exists, skipping: ' + args.grader + ' grading ' + args.writer + ' (' + args.essay_type + ') assignment ' + str(args.assignment))
            return
        
        #1: Set up model, and load essay
        essay_text, writer_name = Util.load_essay_from_data(args.assignment, args.essay_type, writer=writer_target)
        
        #2. Load essay and rubric
        essay = Util.create_essay(args.assignment)
        rubric = Rubric(args.rubric)
        essay.essay_text = essay_text

        #3. Grade and Save
        data = grader_model.score(essay, rubric, writer=writer_name, essay_type=args.essay_type)

        data['writer'] = writer_name 
        data['rubric'] = args.rubric
        data['scored_essay_text'] = essay_text

        Util.save_data(data, args.assignment)

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