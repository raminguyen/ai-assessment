import json
import pandas as pd
import os

# Load data
data_path = os.path.join('..','data', 'data.json')

with open(data_path, 'r') as f:
    data = json.load(f)

rows = []

for assignment_key, operations in data.items():
    for op in operations:
        # Get essay text - prioritize scored_essay_text, fall back to result
        essay_text = op.get('scored_essay_text') or op.get('result', '')
        if essay_text and len(essay_text) > 500:
            essay_text = essay_text[:500] + "..."
        
        row = {
            'Assignment': assignment_key,
            'Command': op.get('command'),
            'Model/Grader': op.get('model') or op.get('grader'),
            'Writer': op.get('writer'),
            'Essay Name': op.get('essay_name'),
            'Essay Type': op.get('essay_type'),
            'Rubric': op.get('rubric', ''),
            'Time (mins)': op.get('time_minutes'),
            'Timestamp': op.get('timestamp'),
            'Result': op.get('result', ''),
            'Essay Text': essay_text
        }
        rows.append(row)

# Create DataFrame
df = pd.DataFrame(rows)

# Display
print(df.to_string(index=False))

csv_path = os.path.join('..','data', 'data.csv')


# Save to CSV
df.to_csv(csv_path, index=False)

print('\nSaved to data.csv')
