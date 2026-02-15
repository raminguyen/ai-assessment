import json
import pandas as pd
import os
import glob

rows = []

data_path = os.path.join('..', 'data')

# Get all rubric folders (critical_thinking, oral_communication, etc)
for rubric_folder in os.listdir(data_path):
    rubric_path = os.path.join(data_path, rubric_folder)
    
    # Skip if not a directory
    if not os.path.isdir(rubric_path):
        continue
    
    # Get all .json files in each rubric folder
    json_files = glob.glob(os.path.join(rubric_path, '*.json'))
    
    for filepath in json_files:
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Extract essay text (use scored_essay_text for scores, result for others)
            essay_text = data.get('scored_essay_text') or data.get('result', '')
            if essay_text and len(essay_text) > 500:
                essay_text = essay_text[:500] + '...'
            
            # Extract filename info
            filename = os.path.basename(filepath)
            
            # Build row with all available data
            row = {
                'Rubric': rubric_folder,
                'Essay Name': data.get('essay_name', 'Unknown'),
                'Command': data.get('command', 'Unknown'),
                'Model': data.get('model', ''),
                'Grader': data.get('grader', ''),
                'Writer': data.get('writer', ''),
                'Essay Type': data.get('essay_type', ''),
                'Folder': data.get('folder', rubric_folder),
                'Time (mins)': data.get('time_minutes', ''),
                'Timestamp': data.get('timestamp', ''),
                'Result Preview': essay_text,
                'Filename': filename
            }
            rows.append(row)
        
        except json.JSONDecodeError:
            print(f'Error decoding JSON: {filename}')
        except Exception as e:
            print(f'Error processing {filename}: {str(e)}')

# Create DataFrame
df = pd.DataFrame(rows)

# Sort by Rubric, Essay Name, Command
df = df.sort_values(by=['Rubric', 'Essay Name', 'Command']).reset_index(drop=True)

# Save to CSV
csv_path = os.path.join('..', 'data', 'alldata.csv')
os.makedirs(os.path.dirname(csv_path), exist_ok=True)
df.to_csv(csv_path, index=False)

print('\n✓ Processed ' + str(len(df)) + ' files')
print('✓ Rubrics found: ' + str(df['Rubric'].nunique()))
print('✓ Essays found: ' + str(df['Essay Name'].nunique()))
print('✓ Commands found: ' + str(df['Command'].nunique()))
print('✓ Saved to alldata.csv')