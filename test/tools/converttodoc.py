import json
import os
import glob
from docx import Document

def main():
    """Convert individual result files to Word documents"""

    data_path = os.path.join('..', 'data')
    
    # Get all .json files from rubric folders
    for rubric in os.listdir(data_path):
        rubric_path = os.path.join(data_path, rubric)
        if not os.path.isdir(rubric_path):
            continue
        
        # Get all .json files (generate, tune, score)
        json_files = glob.glob(os.path.join(rubric_path, '*.json'))
        
        # Also get generate files from data/ and put in rubric docs
        json_files += glob.glob(os.path.join(data_path, '*generate*.json'))
        
        docs_folder = os.path.join(rubric_path, 'docs')
        os.makedirs(docs_folder, exist_ok=True)
        
        for filepath in json_files:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Skip score files
            command = data.get('command', 'unknown')
            if command == 'score':
                continue
            
            result = data.get('result', '')
            if not result:
                continue
            
            filename = os.path.basename(filepath).replace('.json', '.docx')
            doc = Document()
            doc.add_paragraph(result)
            doc_path = os.path.join(docs_folder, filename)
            doc.save(doc_path)
            print('Saved: ' + filename)
    
    print('All documents saved!')

if __name__ == "__main__":
    main()