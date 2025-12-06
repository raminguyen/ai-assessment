from utils import*
import sys

chatgpt = "gpt-4.1"
gemini = "gemini-3-pro-preview"
claude = "claude-sonnet-4-5"
grok = "grok-4-1-fast-reasoning"


prompt_1_write, prompt_2_grade, base_direction, rubric = load_prompts()



#1. chatgpt generates no rubric, other model grades.
run_pipeline(write_model=chatgpt, 
             prompt_1=prompt_1_write,
             grade_model=[gemini, claude, grok], 
             description= "chatgpt write essay with no rubric",
             rubric=None)

#2. chatgpt generates with rubric, other models grades. 
run_pipeline(write_model=chatgpt, 
             prompt_1=prompt_1_write,
             grade_model=[gemini, claude, grok], 
             description= "chatgpt write essay with no rubric",
             rubric=rubric)

