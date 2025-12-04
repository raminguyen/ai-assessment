import os
import json
from docx import Document   # pip install python-docx

# base folder
base_dir = os.path.dirname(os.path.abspath(__file__))

folder = os.path.join(base_dir, "tuned_essay3")

# list all docx files in that folder
files = [f for f in os.listdir(folder) if f.endswith(".docx")]

for file in files:
    input_path = os.path.join(folder, file)

    # read docx text
    doc = Document(input_path)
    parts = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    # merge into one clean block of text
    merged = " ".join(parts)
    merged = " ".join(merged.split())  # removes extra spaces

    # output json file name
    output_path = os.path.join(
        folder,
        file.replace(".docx", ".json")
    )

    # write json
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            {"source": file, "content": merged},
            f,
            indent=2,
            ensure_ascii=False
        )

    print(f"Converted → {output_path}")
