import json
import pandas as pd
import os
import glob

rows = []

data_path = os.path.join('..', 'data')

# Get all .json files from data/ folder (generate files)
json_files = glob.glob(os.path.join(data_path, '*.json'))

for filepath in json_files:
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    essay_text = data.get('scored_essay_text') or data.get('result', '')
    if essay_text and len(essay_text) > 500:
        essay_text = essay_text[:500] + "..."
    
    filename = os.path.basename(filepath)
    assignment = filename.split('_')[1]
    
    row = {
        'Assignment': 'assignment_' + assignment,
        'Command': data.get('command'),
        'Model/Grader': data.get('model') or data.get('grader'),
        'Writer': data.get('writer'),
        'Essay Type': data.get('essay_type'),
        'Rubric': '',
        'Time (mins)': data.get('time_minutes'),
        'Timestamp': data.get('timestamp'),
        'Result': data.get('result', ''),
        'Essay Text': essay_text
    }
    rows.append(row)

# Get all rubric folders
for rubric in os.listdir(data_path):
    rubric_path = os.path.join(data_path, rubric)
    if not os.path.isdir(rubric_path):
        continue
    
    # Get all .json files in rubric folder
    json_files = glob.glob(os.path.join(rubric_path, '*.json'))
    
    for filepath in json_files:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        essay_text = data.get('scored_essay_text') or data.get('result', '')
        if essay_text and len(essay_text) > 500:
            essay_text = essay_text[:500] + "..."
        
        filename = os.path.basename(filepath)
        assignment = filename.split('_')[1]
        
        row = {
            'Assignment': 'assignment_' + assignment,
            'Command': data.get('command'),
            'Model/Grader': data.get('model') or data.get('grader'),
            'Writer': data.get('writer'),
            'Essay Type': data.get('essay_type'),
            'Rubric': rubric,
            'Time (mins)': data.get('time_minutes'),
            'Timestamp': data.get('timestamp'),
            'Result': data.get('result', ''),
            'Essay Text': essay_text
        }
        rows.append(row)

df = pd.DataFrame(rows)


csv_path = os.path.join('..', 'data', 'alldata.csv')
df.to_csv(csv_path, index=False)
print('\nSaved to alldata.csv')