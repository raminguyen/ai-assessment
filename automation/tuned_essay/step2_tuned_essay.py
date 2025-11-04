import os

os.environ["BROWSER_USE_CONFIG_DIR"] = os.path.join(os.getcwd(), "browser_config")

from browser_use import Agent, ChatGoogle, ChatOpenAI, Browser
from dotenv import load_dotenv
import sys 
import json
import asyncio
from pydantic import BaseModel 
from jsonresults import*

#Define a path

# 2️⃣ Create Chrome profile

class AIrunner:
    def __init__(self, base_direction=None, argument=None, aacu_rubric_path=None,
                 email=None, password=None, assignment_number=1,
                 final_result_data=None, aacu_rubric_data=None):

        self.base_direction = base_direction          
        self.argument = argument                      
        self.aacu_rubric_path = aacu_rubric_path      

        self.email = email
        self.password = password
        self.provider = None
        self.model_name = None
        self.url = None
        self.assignment_number = assignment_number
        self.aacu_rubric_data = aacu_rubric_data
        self.final_result_data = final_result_data

    #Step 1: get model
    def getllms(self):
        
        self.provider == "gemini"
        self.model_name = "gemini-2.5-flash"

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

    def prepare_second_prompt(self):

        essay_dir = os.path.join(
            self.base_direction,
            "..",
            f"essay_{self.argument.essay}",
            self.argument.folder
        )

        essay_dir = os.path.abspath(essay_dir)

        final_result_path = os.path.join(essay_dir, "final_extracted.json")

        print("AACU", self.aacu_rubric_path)
        print("essay direction", essay_dir)
        print("final result", final_result_path)

        with open(self.aacu_rubric_path, "r", encoding="utf-8") as f:
            aacu_rubric_data = json.load(f)

        with open(final_result_path, "r", encoding="utf-8") as f:
            final_result_data = json.load(f)

        data = {**aacu_rubric_data, **final_result_data}

        second_prompt = ". ".join([f"{key}: {value}" for key, value in data.items()])

        second_prompt = re.sub(r"[#*\\{}]", "", second_prompt).replace("\n", " ").strip()

        # print(len(second_prompt.split()))

        self.second_prompt = second_prompt
        
        return second_prompt


    #2. Define hyperparameters and paths

    #Step 2: Send prompt  
    def send_prompt(self, prompt, website):

        words = self.second_prompt.split()

        n = len(words)

        parts = []
        start = 0

        indices = [n * i // 6 for i in range(1, 6)]

        for end in indices + [n]:
            parts.append(" ".join(words[start:end]))
            start = end

        part1, part2, part3, part4, part5, part6 = parts

        followup_prompt = """
        
        Generate a fully revised final version of the essay to achieve a full 20/20 score.

        Also, please explain what changes were made in the essay to reach a perfect 20/20 based on the AAC&U rubric.

        """


        # if website == "chatgpt":

        #     prompt = f"""

        #     Follow this instructions step by step:

        #     1) Go to {self.url}

        #     2) Click "Sign in". Use:

        #         - Email: {self.email}
            
        #     3) Click Next, choose passkey, after that, click Continue or Next.

        #     4) Wait for 20 seconds for user log in with their security codes.

        #     5) Paste this prompt {part1}.

        #     6) Paste this prompt {part2}.

        #     7) Paste this prompt {part3}.

        #     8) Paste this prompt {part4}.

        #     9) Paste this prompt {part5}.

        #     10) Enter to submit the prompt.

        #     11) Extract all responses in 40 seconds.

        #     12) Paste this prompt {followup_prompt}.

        #     13) Wait for 60 seconds for the response to be generated. 
            
        #     14) Extract all responses in 40 seconds.

        #     15) End the session.

        #     """

        #     return prompt
        
        if website == "gemini":
            
            prompt = f"""

            Follow this instructions step by step:

            1) Go to {self.url}

            2) Click "Sign in". Use:

                - Email: {self.email}
            
            3) Click Next, choose passkey, after that, click Continue or Next.

            4) Wait for 20 seconds for user log in with their security codes.

            5) Paste this prompt {part1}.

            6) Paste this prompt {part2}.

            7) Paste this prompt {part3}.

            8) Paste this prompt {part4}.

            9) Paste this prompt {part5}.

            10) Paste this prompt {part6}.

            11) Enter to submit the prompt.

            12) Extract all responses in 40 seconds.

            13) Paste this prompt {followup_prompt}. Key "Enter" to submit.

            14) Wait for 60 seconds for the response to be generated. 

            15) Extract all responses in 40 seconds.

            16) Click to open a canvas "Detailed 20/20 Rubric Evaluation" and extract all responses in 15 seconds.

            16) End the session.

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

        try:
            loop = asyncio.get_event_loop()
            close_fn = getattr(getattr(llm, "client", llm), "close", None)
            if close_fn:
                loop.run_until_complete(close_fn())
        except Exception as e:
            print(f"[Warning] Failed to close session: {e}")

        save_result_as_json(result, filename="final_result.json", provider=self.provider, essay_number=self.argument.essay)











    
            



    

