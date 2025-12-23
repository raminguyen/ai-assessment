from ai_assessment import Rubric, Util, ModelChatGPT, ModelClaude, ModelGemini3ProPreview, ModelGrok

class Runner:
    def __init__(self):
        self.all_models = {
            "gemini": ModelGemini3ProPreview(),
            "chatgpt": ModelChatGPT(),
            "claude": ModelClaude(),
            "grok": ModelGrok()
        }
    
    def generate(self, model, assignment, folder):
    
        gen_model = self.all_models[model]
        rubric = folder

        if Util.check_data_exists(assignment, 'generate', model, rubric=rubric):
            print('Already exists, skipping: ' + model + ' generate assignment ' + str(assignment))
            return

        essay = Util.create_essay(assignment, rubric_folder=folder)
        essay.load_prompt(assignment) 
        data = gen_model.generate(essay)
        Util.save_individual_file(data, assignment, 'generate', model, rubric=rubric)


    def tune(self, model, assignment, rubric):

        tune_model = self.all_models[model]

        if Util.check_data_exists(assignment, 'tune', model, rubric=rubric):
            print('Already exists, skipping: ' + model + ' tune assignment ' + str(assignment))
            return

        essay = Util.create_essay(assignment)
        essay.load_prompt(assignment)  # ← ADD THIS

        rubric_obj = Rubric(rubric)

        data = tune_model.tune(essay, rubric_obj)
        data['rubric'] = rubric
        data['folder'] = 'critical_thinking'

        Util.save_individual_file(data, assignment, 'tune', model, rubric=rubric)

    def score(self, grader, rubric, filename, assignment):

        grader_model = self.all_models[grader]
        
        essay_text, writer_name, essay_type = Util.load_essay_from_data(filename, rubric=rubric)

        if Util.check_data_exists(assignment, 'score', grader, essay_type=essay_type, writer=writer_name, rubric=rubric):
            print('Already exists, skipping: ' + grader + ' scoring ' + essay_type + ' assignment ' + str(assignment))
            return
        
        essay = Util.create_essay(assignment)
        essay.load_prompt(assignment)  # ← ADD THIS
        
        rubric_obj = Rubric(rubric)
        essay.essay_text = essay_text

        data = grader_model.score(essay, rubric_obj, writer=writer_name, essay_type=essay_type)

        data['rubric'] = rubric
        data['folder'] = 'critical_thinking'  # ← ADD THIS
        data['scored_essay_text'] = essay_text
        data['essay_type'] = essay_type

        Util.save_individual_file(data, assignment, 'score', grader, essay_type=essay_type, rubric=rubric, writer=writer_name)
        