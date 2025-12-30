import os
import json
from datetime import datetime
import strip_markdown
from docx import Document
from ai_assessment import Essay
import glob
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
    def create_essay(assignment, rubric_folder="critical_thinking"):
        """Create and load essay"""
        essay = Essay(
            name='Assignment_' + str(assignment),
            rubric_folder=rubric_folder
        )
        return essay
    
    
    @staticmethod
    def save_data(data, assignment):
        """Add assignment and save to file"""
        data['assignment'] = assignment
        Util.save_to_file('data.json', data)

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

    def build_filename(assignment, command, short_model, essay_type=None, short_writer=None):

        """Build filename based on command"""
        base = "a" + str(assignment)
        essay_abbr = "gen" if essay_type == "generate" else "tune"

        filename_map = {
            'generate': base + "_gen_" + short_model + ".json",
            'tune': base + "_tune_" + short_model + ".json",
            'reflection': base + "_reflection_" + short_model + ".json",
            'score': base + "_" + essay_abbr + "_" + short_writer + "_score_" + short_model + ".json" if essay_type and short_writer else None,
        }

        return filename_map.get(command, base + "_" + short_model + ".json")

    @staticmethod
    def save_individual_file(data, assignment, command, model_name, essay_type=None, rubric=None, writer=None):
        """Save individual JSON file for each command in rubric folder"""
        
        if not rubric:
            rubric = 'critical_thinking'    
        
        folder = os.path.join('..', 'data', rubric)

        os.makedirs(folder, exist_ok=True)
        
        # Map full names to short names
        name_map = {
            "gpt-5.2-2025-12-11": "chatgpt",
            "grok-4-1-fast-reasoning": "grok",
            "gemini-3-pro-preview": "gemini",
            "claude-sonnet-4-5-20250929": "claude"
        }
        
        short_model = name_map.get(model_name, model_name)

        short_writer = name_map.get(writer, writer) if writer else None

        filename = Util.build_filename(assignment, command, short_model, essay_type, short_writer)

        filepath = os.path.join(folder, filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print('Saved: ' + filepath)

    @staticmethod
    def load_essay_from_data(filename, rubric=None):
        """Load essay from individual file"""
        
        folder = os.path.join('..', 'data', rubric)

        filepath = os.path.join(folder, filename)
        
        print('Looking for: ' + filepath)  
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        if 'gen' in filename:
            essay_type = 'generate'

        elif 'tune' in filename:
            essay_type = 'tune'
            
        else:
            essay_type = 'generate'
        
        return data.get("result"), data.get("model"), essay_type

    @staticmethod
    def check_data_exists(assignment, command, model_name, essay_type=None, writer=None, rubric=None):
        """Check if individual file exists"""
        
        name_map = {
            "gpt-5.2-2025-12-11": "chatgpt",
            "grok-4-1-fast-reasoning": "grok",
            "gemini-3-pro-preview": "gemini",
            "claude-sonnet-4-5-20250929": "claude"
        }
        
        short_model = name_map.get(model_name, model_name)
        short_writer = name_map.get(writer, writer) if writer else None
        
        filename = Util.build_filename(assignment, command, short_model, essay_type, short_writer)
        folder = os.path.join('..', 'data', rubric)

        filepath = os.path.join(folder, filename)
        return os.path.exists(filepath)