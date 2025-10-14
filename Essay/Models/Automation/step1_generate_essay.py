from browser_use import Agent, ChatGoogle
from dotenv import load_dotenv
import os
import sys 
import json
import asyncio
from pydantic import BaseModel 
from jsonresults import*

class AIrunner:
    def __init__(self, email=None, password=None):
        self.email = email
        self.password = password
        self.provider = None
        self.model_name = None
        self.url = None

    #Step 1: get model
    def getllms(self):
        
        self.provider == "gemini"
        
        self.model_name = "gemini-2.5-flash"

        return ChatGoogle(model=self.model_name)
    
    #Step 2: open target website

    def target_website(self, website):
        target_website = {
            "chatgpt": "https://chatgpt.com",
            "gemini": "https://gemini.google.com/app",
            "copilot": "https://copilot.microsoft.com/",
            "claude": "https://claude.ai/login"
        }
        self.url = target_website.get(website, None)

    #Step 2: Send prompt  
    def send_prompt(self, prompt, interactive=True):

        if interactive:
            prompt = f"""

            Follow this instructions step by step:

            1) Go to {self.url}
            2) Click "Sign in". Use:
                - Email: {self.email}
                - Password: {self.password}
            3) Wait for 15 seconds for user log in with their security codes.
            4) Paste this prompt {first_prompt} and send:
            5) Wait for 15 seconds for the response to be generated.
            6) Wait for 30 seconds for the response to be extracted.
            6) Grab the response text. 

            """

            return prompt


      #Step 3: run agent
    def agent(self, prompt, interactive=None):
        llm = self.getllms()
        agent = Agent(task=prompt, llm=llm)
        result = agent.run_sync()
        result = result.action_results()
        result = result 
        agent.close()
        save_result_as_json(result)
        
# Main code

#1. Define hyperparameters and paths

prompts_json_path = "/Users/ramihuunguyen/Documents/PhD/AI-Assessment/Essay/Models/Automation/prompts1.json"

#sys.exit() #stop execution here for now

with open(prompts_json_path, "r", encoding='utf-8') as f:
    first_prompt = str(json.load(f)['step1_first_prompt'])

#1a: Load email and password.

load_dotenv()

EMAIL = os.getenv("EMAIL")

PASSWORD  = os.getenv("PASS")
    
#2.: Initialize AIrunner

runner = AIrunner(email=EMAIL, password=PASSWORD)

#3.: Set a target website

runner.target_website("chatgpt")

#4: Generate an essay

generate_essay = runner.send_prompt(first_prompt, interactive=True)

result = runner.agent(generate_essay)










    
            



    

