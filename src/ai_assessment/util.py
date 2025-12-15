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
    def load_essay_from_data(filename, rubric=None):
        """Load essay from individual file"""
        
        # Only generate files are in data/ folder
        # Tune and score files are in rubric subfolder
        if 'generate' in filename:
            folder = os.path.join('..', 'data')
        elif rubric:
            folder = os.path.join('..', 'data', rubric)
        else:
            folder = os.path.join('..', 'data')
        
        filepath = os.path.join(folder, filename)
        
        print('Looking for: ' + filepath)  
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Extract essay type from filename
        essay_type = filename.split('_')[2]
        
        return data.get("result"), data.get("model"), essay_type
                    
    def check_data_exists(assignment, command, model_name, essay_type=None, writer=None, rubric=None):
        """Check if individual file exists"""
        
        if command == 'score' and essay_type and writer:
            filename = "assignment_" + str(assignment) + "_" + command + "_" + model_name + "_" + essay_type + "_" + writer + ".json"
        else:
            filename = "assignment_" + str(assignment) + "_" + command + "_" + model_name + ".json"
        
        if rubric:
            folder = os.path.join('..', 'data', rubric)
        else:
            folder = os.path.join('..', 'data')
        
        filepath = os.path.join(folder, filename)

        return os.path.exists(filepath)
                
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

    @staticmethod
    def save_individual_file(data, assignment, command, model_name, essay_type=None, rubric=None, writer=None):
        """Save individual JSON file for each command in rubric folder"""
        
        folder = os.path.join('..', 'data', rubric) if rubric else os.path.join('..', 'data')
        os.makedirs(folder, exist_ok=True)
        
        # Map full names to short names
        name_map = {
            "gpt-5.2-2025-12-11": "chatgpt",
            "grok-4-1-fast-reasoning": "grok",
            "gemini-3-pro-preview": "gemini",
            "claude-sonnet-4-5-20250929": "claude"
        }
        
        # Use short name if available
        short_model = name_map.get(model_name, model_name)
        short_writer = name_map.get(writer, writer) if writer else None
        
        if command == 'score' and essay_type and short_writer:
            filename = "assignment_" + str(assignment) + "_" + command + "_" + short_model + "_" + essay_type + "_" + short_writer + ".json"
        else:
            filename = "assignment_" + str(assignment) + "_" + command + "_" + short_model + ".json"
        
        filepath = os.path.join(folder, filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print('Saved: ' + filepath)