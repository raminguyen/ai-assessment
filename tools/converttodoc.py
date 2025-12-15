import json
import os
from docx import Document

@staticmethod
def main():
    """Convert all results in data.json to Word documents"""

    # Load data
    data_path = os.path.join('..', 'data', 'data.json')

    with open(data_path, 'r') as f:
        all_data = json.load(f)
    
    # Create docs folder
    docs_folder = os.path.join('..', 'data','docs')
    os.makedirs(docs_folder, exist_ok=True)
    
    # Loop through all assignments
    for assignment_key, operations in all_data.items():
        for op in operations:
         
            command = op.get('command', 'unknown')
            if command == 'score':
                continue
            
            # Get result text
            result = op.get('result', '')
            if not result:
                continue
            
            # Build filename
            model = op.get('model', 'unknown')
            
            if command == 'generate':
                filename = assignment_key + '_' + model + '_generate.docx'
            elif command == 'tune':
                filename = assignment_key + '_' + model + '_tuned.docx'
            else:
                filename = assignment_key + '_' + model + '_' + command + '.docx'
            
            # Create document
            doc = Document()
            doc.add_paragraph(result)
            
            # Save
            doc_path = os.path.join(docs_folder, filename)
            doc.save(doc_path)
            print('Saved: ' + filename)
    
    print('All documents saved to: ' + docs_folder)

if __name__ == "__main__":
    main()