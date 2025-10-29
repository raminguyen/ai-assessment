import os

os.environ["BROWSER_USE_CONFIG_DIR"] = os.path.join(os.getcwd(), "browser_config")

from browser_use import Agent, ChatGoogle, ChatOpenAI, Browser
from dotenv import load_dotenv
import sys 
import json
import asyncio
from pydantic import BaseModel 
from jsonresults import*

# 2️⃣ Create Chrome profile


class AIrunner:
    def __init__(self, email=None, password=None, assignment_number=1,
                 final_result_data=None, aacu_rubric_data=None):
        self.email = email
        self.password = password
        self.provider = None
        self.model_name = None
        self.url = None
        self.assignment_number = assignment_number
        assignment_key = f"assignment_{self.assignment_number}_prompt"
        self.final_result_data = final_result_data
        self.aacu_rubric_data = aacu_rubric_data


    #Step 1: get model
    def getllms(self):
        
        self.provider == "gemini"
        self.model_name = "gemini-flash-latest"
        return ChatGoogle(model=self.model_name)
    
    # def getllms(self):
    #     # set provider and model
    #     self.provider = "chatgpt"
    #     self.model_name = "gpt-5-2025-08-07"

    #     OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    #     # create ChatOpenAI instance
    #     llm = ChatOpenAI(model=self.model_name, api_key=OPENAI_API_KEY)
    #     llm.model = self.model_name 

    #     return llm
    
    #Step 2: open target website

    def target_website(self, website):
        target_website = {
            "chatgpt": "https://chatgpt.com",
            "gemini": "https://gemini.google.com/app",
            "copilot": "https://copilot.microsoft.com/",
            "claude": "https://claude.ai/login"
        }
        self.url = target_website.get(website, None)

    #2. Define hyperparameters and paths

    #Step 2: Send prompt  
    def send_prompt(self, prompt, interactive=True):

        if interactive:
            prompt = f"""

            Follow this instructions step by step:

            1) Go to {self.url}
            2) Click "Sign in". Use:
                - Email: {self.email}
                - Password: {self.password}
            3) Wait for 20 seconds for user log in with their security codes.
            4) Paste this prompt {self.assignment_prompt} and click key enter.
            5) Wait for 15 seconds before move to the next step.
            5) Wait for 15 seconds for the response to be generated.
            6) Wait for 90 seconds for the response to be extracted. Ensure extracted responses exactly. 
            6) Grab the response text. 

            """

            return prompt


      #Step 3: run agent


    def agent(self, prompt, interactive=None):
        
        llm = self.getllms()


        # browser = Browser(
        #     executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        #     user_data_dir='~/Library/Application Support/Google/Chrome'

        #     )

        agent = Agent(task=prompt, llm=llm, browser=None)

        result = agent.run_sync()
        result = result.action_results()
        result = result 
        agent.close()
        save_result_as_json(result, filename="final_result.json", provider=self.provider, assignment_number=self.assignment_number)











    
            



    

