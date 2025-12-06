from utils import*
import sys

chatgpt = "gpt-4.1"
gemini = "gemini-3-pro-preview"
claude = "claude-sonnet-4-5"

#1. chatgpt generates, other model grades.
#run_pipeline(write_model=chatgpt, grade_model=gemini, description="chatgpt")
#test done


#2. gemini generates, other model grades.
#run_pipeline(write_model=gemini, grade_model=chatgpt, description="gemini")

#3. claude generates, other model grades.
run_pipeline(write_model=claude, grade_model=chatgpt, description="claude")