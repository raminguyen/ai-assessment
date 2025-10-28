from step1_generate_essay import AIrunner
from browser_use import Agent, ChatGoogle
from dotenv import load_dotenv
import os, json
import argparse

#1: Load email and password.

load_dotenv()

EMAIL = os.getenv("EMAIL")

PASSWORD  = os.getenv("PASS")


base_direction = os.path.dirname(os.path.abspath(__file__))

prompts_json_path = os.path.join(base_direction, "assignmentprompt.json")

with open(prompts_json_path, "r", encoding='utf-8') as f:
    assignment_prompt = str(json.load(f)['assignment_1_prompt'])

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

    argument = parser.parse_args()

    #2. Define email and password
    bot = AIrunner(email=EMAIL, password=PASSWORD, assignment_number=argument.assignment) 

    #3a: Define a website
    
    bot.provider = argument.website

    bot.target_website(argument.website) #target website

     #3b: Define an assignment

    base_direction = os.path.dirname(os.path.abspath(__file__))
    assignment_prompt_path = os.path.join(base_direction, "assignmentprompt.json")

    with open(assignment_prompt_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assignment_number = argument.assignment
    assignment_key = f"assignment_{assignment_number}_prompt"
    assignment_prompt = data.get(assignment_key, "Assignment prompt not found.")


    #4:Send prompt
    prompt = bot.send_prompt(assignment_prompt, interactive=True)

    #5: Run agent
    bot.agent(prompt)


    
