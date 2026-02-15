import time
from datetime import datetime


class Model:
    def __init__(self, model_name):
        self.name = model_name
        self.client = None
    
    def generate(self, essay, rubric_folder=None):

        print("Generating an essay")
        print("Generation prompt:", essay.write_prompt)

        # Save prompt
        # with open('generation_prompt.txt', 'w') as f:
        #     f.write("=" * 10 + "\nGENERATION PROMPT\n" + "=" * 10 + "\n\n")
        #     f.write(essay.write_prompt)
        
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
            "folder": essay.rubric_folder,
            "prompt": essay.write_prompt,
            "result": result,
            "time_minutes": round(essay.time / 60, 2),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return data

    def generate_iterative(self, essay, rubric_folder=None):

        print("Generating essay (iterative 2-step)")
        print("Step 1 prompt:", essay.context_prompt)
        print("Step 2 prompt:", essay.generate_prompt)

        start = time.time()

        # Step 1: Send context, get analysis
        step1_result = self.api_call(essay.context_prompt)
        print("Step 1 complete, got analysis")
        time.sleep(5)

        # Step 2: Send generation instruction in same conversation
        messages = [
            {"role": "user", "content": essay.context_prompt},
            {"role": "assistant", "content": step1_result},
            {"role": "user", "content": essay.generate_prompt}
        ]
        result = self.api_call_multi(messages)

        essay.essay_text = result
        essay.status = 1
        essay.time = time.time() - start
        print(f"Done in {essay.time/60:.2f} mins")
        time.sleep(5)

        data = {
            "command": "generate",
            "model": self.name,
            "essay_name": essay.name,
            "folder": essay.rubric_folder,
            "prompt": essay.context_prompt,
            "prompt_step2": essay.generate_prompt,
            "step1_result": step1_result,
            "result": result,
            "time_minutes": round(essay.time / 60, 2),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return data

    def tune(self, essay, rubric):

        print("Tuning with rubric")
        # Use template
        tuning_prompt = essay.tuning_prompt
        tuning_prompt = tuning_prompt.replace("{ASSIGNMENT_PROMPT}", essay.write_prompt)
        tuning_prompt = tuning_prompt.replace("{rubric}", rubric.text)
        print("Tuning prompt:", tuning_prompt)

        # Save prompt
        # with open('tuning_prompt.txt', 'w') as f:
        #     f.write("=" * 10 + "\nTUNING PROMPT\n" + "=" * 10 + "\n\n")
        #     f.write(tuning_prompt)

        start = time.time()
        result = self.api_call(tuning_prompt)
        
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
        # Use template
        score_prompt = essay.grade_prompt.replace("{rubric}", rubric.text) + essay.essay_text
        print("Score prompt:", score_prompt)

        # Save prompt
        # with open('score_prompt.txt', 'w') as f:
        #     f.write("=" * 10 + "\nSCORE PROMPT\n" + "=" * 10 + "\n\n")
        #     f.write(score_prompt)

        start = time.time()
        result = self.api_call(score_prompt)

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
            "folder": essay.rubric_folder,
            "rubric": essay.rubric_folder,
            "scored_essay_text": essay.essay_text,
            "result": result,
            "time_minutes": round(elapsed / 60, 2),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return data

    def reflect(self, essay, original_essay, tuned_essay, rubric):

        print("Generating reflection")
        start = time.time()

        # Use template
        reflection_prompt = essay.reflection_prompt
        # Remove intro from assignment prompt
        assignment_prompt = essay.write_prompt.replace('You are an undergrad student in the first semester.\n\n', '')
        assignment_prompt = assignment_prompt.replace('You are an undergrad student in the first semester. ', '')
        reflection_prompt = reflection_prompt.replace("{ASSIGNMENT_PROMPT}", assignment_prompt)
        reflection_prompt = reflection_prompt.replace("{original essay}", original_essay)
        reflection_prompt = reflection_prompt.replace("{tuned essay}", tuned_essay)
        reflection_prompt = reflection_prompt.replace("{rubric}", rubric.text)
        print("Reflection prompt:", reflection_prompt)

        # Save prompt
        # with open('reflection_prompt.txt', 'w') as f:
        #     f.write("=" * 10 + "\nREFLECTION PROMPT\n" + "=" * 10 + "\n\n")
        #     f.write(reflection_prompt)


        result = self.api_call(reflection_prompt)

        essay.reflection_result = result
        essay.status = 4
        elapsed = time.time() - start
        print(f"Done in {elapsed/60:.2f} mins")
        time.sleep(5)

        # Create and return data
        data = {
            "command": "reflection",
            "writer": self.name,
            "essay_name": essay.name,
            "folder": essay.rubric_folder,
            "result": result,
            "time_minutes": round(elapsed / 60, 2),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return data

