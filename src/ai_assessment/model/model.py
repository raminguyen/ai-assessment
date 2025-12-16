import time
from datetime import datetime


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
    
