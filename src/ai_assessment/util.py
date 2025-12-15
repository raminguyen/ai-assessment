import os
import json
from datetime import datetime
import strip_markdown
from docx import Document
from ai_assessment import Essay

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
    def load_essay(filename):
        
        file_path = os.path.join(Util.OUTPUT_FOLDER, filename)
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return data["result"]
    
        
    
    @staticmethod
    def create_essay(assignment):
        """Create and load essay"""
        essay = Essay('Essay_' + str(assignment))
        essay.load_prompt(assignment)
        return essay
    
    @staticmethod
    def save_data(data, assignment):
        """Add assignment and save to file"""
        data['assignment'] = assignment
        Util.save_to_file('data.json', data)


    @staticmethod
    def load_essay_from_data(assignment, essay_type, writer=None):

        """ Get essay text from data.json """

        filepath = os.path.join('..', 'data', 'data.json')
        
        # 1. map user input
        name_map = {
            "chatgpt": "gpt", 
            "claude": "claude",
            "gemini": "gemini",
            "grok": "grok"
        }

        search_term = name_map.get(writer, writer)

        # 2. Load data.json
        filepath = os.path.join('..', 'data', 'data.json')
        with open(filepath, 'r') as f:
            all_data = json.load(f)

        # 3. Find matching essay
        operations = all_data['assignment_' + str(assignment)] 
        
        for op in operations:
            # Check if command matches (e.g., 'generate', or 'tune')
            if op.get("command") != essay_type:
                continue

            # Check if writer matches 
            if writer and search_term not in op.get("model", ""):
                continue
                
            return op["result"], op.get("model")
            

    @staticmethod
    def check_data_exists(assignment, command, model_name, essay_type=None, writer=None, rubric=None):

        """ check if data already exists in data.json"""

        name_map = {
            "chatgpt": "gpt", 
            "claude": "claude",
            "gemini": "gemini",
            "grok": "grok"
        }
        
        search_writer = name_map.get(writer, writer)

        filepath = os.path.join('..', 'data', 'data.json')
        
        if not os.path.exists(filepath):
            return False
            
        with open(filepath, 'r') as f:
            all_data = json.load(f)
            
        #check assignment if exists
        assignment_key = 'assignment_' + str(assignment)

        if assignment_key not in all_data:
            return False

        #find assignment    
        operations = all_data[assignment_key]
        
        for op in operations:

            #command does not match
            if op.get('command') != command:
                continue
            
            #model does not match
            current_model = op.get('grader') if op.get('grader') else op.get('model')

    
            if current_model != model_name:
                continue
                
            if rubric and op.get('rubric') != rubric:
                continue

            #essay type does not match
            if essay_type and op.get('essay_type') != essay_type:
                continue

            if writer and search_writer not in op.get('writer', ''):
                continue
            
            return True
            
        return False
    
    @staticmethod

    def save_to_file(filename, data):

        """Append data to JSON file organized by assignment"""
        
        # Save to data folder
        filepath = os.path.join('..', 'data', filename)
        
        all_data = {}
        
        if os.path.exists(filepath):
            f = open(filepath, 'r')
            content = f.read()
            f.close()
            
            if content:
                all_data = json.loads(content)
        
        # Get assignment key
        assignment_key = 'assignment_' + str(data.get('assignment', 1))

        if assignment_key not in all_data:
            all_data[assignment_key] = []
                    
        # Append to assignment
        all_data[assignment_key].append(data)
        
        f = open(filepath, 'w')
        
        json.dump(all_data, f, indent=2)
        f.close()
        
        print('Saved to: ' + filepath)