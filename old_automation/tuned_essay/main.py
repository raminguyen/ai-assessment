from step2_tuned_essay import AIrunner
from browser_use import Agent, ChatGoogle
from dotenv import load_dotenv
import os, json
import argparse
import sys
import re

#1: Load email and password.

load_dotenv()

EMAIL = os.getenv("EMAIL")

PASSWORD  = os.getenv("PASS")

base_direction = os.path.dirname(os.path.abspath(__file__))

aacu_rubric_path = os.path.join(base_direction, "aacu_rubrics.json")

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
        "-e","--essay",
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

    #sys.exit()

    #2. Define email and password
    bot = AIrunner(
        email=EMAIL,
        password=PASSWORD,
        argument=argument,
        base_direction=base_direction,
        aacu_rubric_path=aacu_rubric_path
    )

    #3a: Define a website
    
    bot.provider = argument.website

    bot.target_website(argument.website) #target website

    #3b: Define an essay
    
    essay_number = argument.essay
    
    essay_key = f"essay_{essay_number}_prompt"


    
    first_prompt = bot.prepare_first_prompt(essay_number)
    


    bot.prepare_second_prompt()

    #import sys
    #sys.exit()  

    #4:Send prompt
    prompt = bot.send_prompt(website=argument.website)

    #5: Run agent
    bot.agent(prompt)


    
