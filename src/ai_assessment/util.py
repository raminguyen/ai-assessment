import os
import json
from datetime import datetime
import strip_markdown
from docx import Document

class Util:
    OUTPUT_FOLDER = "results"
    
    @staticmethod
    def _ensure_folder():
        os.makedirs(Util.OUTPUT_FOLDER, exist_ok=True)
    
    @staticmethod
    def texttojson(text, file_name, essay, rubric=None, writer_model=None, grader_model=None, source_file=None, grade_time=None):
        
        Util._ensure_folder()
        
        # Get time
        time_val = getattr(essay, 'time', grade_time)
        
        data = {
            "essay_name": essay.name,
            "writer_model": writer_model.name if writer_model else None,
            "grader_model": grader_model.name if grader_model else None,
            "time_taken": round(time_val / 60, 2) if time_val else None,
            "loaded_from": source_file,
            "rubric": rubric.text if rubric else None,
            "result": text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        file_path = os.path.join(Util.OUTPUT_FOLDER, file_name)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print("Saved at", file_path)

        return file_path
        
    @staticmethod
    def jsontodoc(json_file, output_name=None):
        json_path = os.path.join(Util.OUTPUT_FOLDER, json_file)
        
        with open(json_path, "r") as f:
            data = json.load(f)
        
        text = data["result"]
        
        if output_name is None:
            output_name = json_file.replace(".json", ".docx")
        
        clean_text = strip_markdown.strip_markdown(text)
        
        doc = Document()
        doc.add_paragraph(clean_text)
        
        docs_folder = os.path.join(Util.OUTPUT_FOLDER, "docs")
        os.makedirs(docs_folder, exist_ok=True)
        output_path = os.path.join(docs_folder, output_name)
        
        doc.save(output_path)
        print("Saved at", output_path)
        return output_path
    
    @staticmethod
    def batch_jsontodoc(json_files):
        for json_file in json_files:
            Util.jsontodoc(json_file)
    
    @staticmethod
    def load_essay(filename):
        
        file_path = os.path.join(Util.OUTPUT_FOLDER, filename)
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return data["result"]
    
    
    @staticmethod
    def grade_all(essay, rubric, graders, writer_model, essay_file, assignment):
       
        """Grade essay with all grader models"""
        grade_files = []

        for name in graders:
            # Run grading for this grader
            graded, grade_time = graders[name].grade(essay, rubric)

            # Create output file for this grader
            grade_file = name + "_grade_essay" + str(assignment) + ".json"

            Util.texttojson(graded, grade_file, essay, rubric, 
                        writer_model=writer_model, 
                        grader_model=graders[name], 
                        source_file=essay_file,
                        grade_time=grade_time)
            grade_files.append(grade_file)
        
        return grade_files