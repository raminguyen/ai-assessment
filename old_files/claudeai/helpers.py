# helpers.py
import os, pathlib, re

# 1. Read file → string
def read_text(path):
    return pathlib.Path(path).read_text(encoding="utf-8", errors="ignore")

# 2. Split string → word tokens
def tokens(text):
    return re.findall(r"\b[\w'-]+\b", text.lower())

# 3. Check if files exist
def check_files(input_dir, files_dict):
    for k, fname in files_dict.items():
        path = pathlib.Path(input_dir) / fname
        print(k, "->", path, "exists:", path.exists())
