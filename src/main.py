import argparse

from ai_assessment import (
    Essay,
    Rubric,
    ModelChatGPT,
    ModelClaude,
    ModelGemini3ProPreview,
    ModelGrok,
    Util
)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser()
    parser.add_argument("writer", choices=["gemini", "chatgpt", "claude", "grok"])
    parser.add_argument('workflow', type=str, choices=["norubric", "withrubric", "both"])
    parser.add_argument('rubric', type=str)  
    parser.add_argument('assignment', type=int)
    args = parser.parse_args()

    #2. Set up models
    all_models = {
        "gemini": ModelGemini3ProPreview(),
        "chatgpt": ModelChatGPT(),
        #"claude": ModelClaude(), #end for now, as server is overloaded.
        "grok": ModelGrok()
    }


    #3. Pick the writer model
    writer_model = all_models[args.writer]

    graders = {}
    for name, model in all_models.items():
        if name != args.writer:
            graders[name] = model

    # Set up essay and rubric
    essay = Essay('Essay_' + str(args.assignment))
    
    rubric = Rubric(args.rubric)

    essay.load_prompt(args.assignment)

    base_folder = 'output/' + 'assignment_' + str(args.assignment) + '/' + args.writer + '/' + args.rubric

    # Decide which workflows to run
    workflows = []
    
    if args.workflow == "both":

        workflows = ["norubric", "withrubric"]
    else:
        workflows = [args.workflow]

    #
    # Without Rubric
    #

    for workflow in workflows:

        if workflow == "norubric":

            Util.OUTPUT_FOLDER = base_folder + '/norubric' 
            
            generated = writer_model.generate(essay)

            essay_file = args.writer + '_generate_essay' + str(args.assignment) + '.json'

            Util.texttojson(generated, essay_file, essay, writer_model=writer_model)
            
            essay.essay_text = Util.load_essay(essay_file)
            grade_files = Util.grade_all(essay, rubric, graders, writer_model, essay_file, args.assignment)
            
            Util.batch_jsontodoc([essay_file] + grade_files)

        #
        # With Rubric
        #
        else:
            Util.OUTPUT_FOLDER = base_folder + '/withrubric'
            
            tuned = writer_model.tune(essay, rubric)

            essay_file = args.writer + '_tuned_essay' + str(args.assignment) + '.json'

            Util.texttojson(tuned, essay_file, essay, rubric, writer_model=writer_model)
        
            essay.essay_text = Util.load_essay(essay_file)

            grade_files = Util.grade_all(essay, rubric, graders, writer_model, essay_file, args.assignment)
            
            Util.batch_jsontodoc([essay_file] + grade_files)

    print("Rami is done.")


if __name__ == "__main__":
    main()