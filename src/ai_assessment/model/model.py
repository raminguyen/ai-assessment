import time
import time


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

        return result
    
    def tune(self, essay, rubric):
        print("Tuning with rubric")
        start = time.time()
        result = self.api_call(rubric.text + essay.write_prompt)
        
        essay.essay_text = result
        essay.status = 2
        essay.time = time.time() - start
        print(f"Done in {essay.time/60:.2f} mins")
        time.sleep(5)

        return result
    
    def grade(self, essay, rubric):

        print("Grading essay")
        start = time.time()
        result = self.api_call(essay.grade_prompt + rubric.text + essay.essay_text)
        
        essay.grade_result = result
        essay.status = 3
        elapsed = time.time() - start
        print(f"Done in {elapsed/60:.2f} mins")
        time.sleep(5)
        
        return result, elapsed