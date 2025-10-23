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

prompts_json_path = os.path.join(base_direction, "prompts1.json")


with open(prompts_json_path, "r", encoding='utf-8') as f:
    first_prompt = str(json.load(f)['step1_first_prompt'])



if __name__ == "__main__":

    #1: Define parse command line argument
    parser = argparse.ArgumentParser(description="Run AI agent for ChatGPT, Gemini, ClaudeAI, or Copilot")

    parser.add_argument(
        "-w", "--website",
        type = str,
        required = True,
        choices = ["chatgpt", "gemini", "claude", "copilot"]
    )
    argument = parser.parse_args()

    #2. Define email and password
    bot = AIrunner(email=EMAIL, password=PASSWORD) 

    #3: Define a website
    
    bot.provider = argument.website
    bot.target_website(argument.website) #target website


    #4:Send prompt
    prompt = bot.send_prompt(first_prompt, interactive=True)

    #5: Run agent
    bot.agent(prompt)


    
