import json
import os

# Base directory
base_dir = "test/test1/data/critical_thinking"

# Files to update
files = [
    "a1_test1_tune_chatgpt.json",
    "a1_test1_tune_gemini.json",
    "a1_test1_tune_claude.json",
    "a1_test1_tune_grok.json"
]

for filename in files:
    filepath = os.path.join(base_dir, filename)

    # Read the file
    with open(filepath, 'r') as f:
        data = json.load(f)

    # Get current prompt (which is just the assignment text)
    current_prompt = data.get('prompt', '')

    # Add the tuning instruction if it's not already there
    if "Now, please write the essay based on the attached rubric" not in current_prompt:
        # Append the tuning instruction
        new_prompt = current_prompt + "\n\nNow, please write the essay based on the attached rubric {rubric}"
        data['prompt'] = new_prompt

        # Write back
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Updated {filename}")
        print(f"New prompt length: {len(new_prompt)}")
    else:
        print(f"Skipped {filename} - already has tuning instruction")

print("\nAll test1 tune files updated!")
