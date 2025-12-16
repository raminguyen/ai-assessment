from ai_assessment import Rubric, Util, ModelChatGPT, ModelClaude, ModelGemini3ProPreview, ModelGrok

class Run:
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