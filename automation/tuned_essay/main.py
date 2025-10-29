from step2_tuned_essay import AIrunner
from browser_use import Agent, ChatGoogle
from dotenv import load_dotenv
import os, json
import argparse
import sys

#1: Load email and password.

load_dotenv()

EMAIL = os.getenv("EMAIL")

PASSWORD  = os.getenv("PASS")


base_direction = os.path.dirname(os.path.abspath(__file__))


if __name__ == "__main__":

    #1: Define parse command line argument
    parser = argparse.ArgumentParser(description="Run AI agent for ChatGPT, Gemini, ClaudeAI, or Copilot")

    parser.add_argument(
        "-w", "--website",
        type = str,
        required = True,
        choices = ["chatgpt", "gemini", "claude", "copilot"]
    )

    parser.add_argument(
        "-a","--assignment",
        type=int,
        required=True,
        choices=[1,2,3],
        help="Select assignment number: 1,2,3"
    )

    parser.add_argument(
        "-f", "--folder",
        type = str,
        required = True,
        choices = ["chatgpt", "gemini", "claude", "copilot"],
        help="Specify folder name for result source: e.g., chatgpt, gemini, copilot, and claude"
    )


    argument = parser.parse_args()

    #Define a path

    aacu_rubric_path = os.path.join(base_direction, "aacu_rubrics.json")

    essay_dir = os.path.join(base_direction, "..", "original_essay", f"essay_{argument.assignment}", argument.folder)

    essay_dir = os.path.abspath(essay_dir)

    final_result_path = os.path.join(essay_dir, "final_extracted.json")

    print("AACU", aacu_rubric_path)
    print("essay direction", essay_dir)
    print("final result", final_result_path)

    with open(aacu_rubric_path, "r", encoding="utf-8") as f:
        aacu_rubric_data = json.load(f)

    with open(final_result_path, "r", encoding="utf-8") as f:
        final_result_data = json.load(f)

   

    data = {**aacu_rubric_data, **final_result_data}

    print(data)

    sys.exit()


    #2. Define email and password
    bot = AIrunner(email=EMAIL,
                   password=PASSWORD, 
                   assignment_number=argument.assignment,
                   aacu_rubric_data=aacu_rubric_data,
                   final_result_data=final_result_data) 

    #3a: Define a website
    
    bot.provider = argument.website

    bot.target_website(argument.website) #target website

    #3b: Define an assignment
    
    assignment_number = argument.assignment
    
    assignment_key = f"assignment_{assignment_number}_prompt"

    data = data.get(assignment_key, "Assignment prompt not found.")

    #4:Send prompt
    prompt = bot.send_prompt(data, interactive=True)

    #5: Run agent
    bot.agent(prompt)


    
