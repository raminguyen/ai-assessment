import os

#os.environ["BROWSER_USE_CONFIG_DIR"] = os.path.join(os.getcwd(), "browser_config")

from browser_use import Agent, ChatGoogle, ChatOpenAI, Browser
from dotenv import load_dotenv
import sys 
import json
import asyncio
from pydantic import BaseModel 
from jsonresults import*
import time 
import shutil

#Define a path

class AIrunner:
    def __init__(self, base_direction=None, argument=None, aacu_rubric_path=None,
                 email=None, password=None, assignment_number=1,
                 final_result_data=None, aacu_rubric_data=None):

        self.base_direction = base_direction          
        self.argument = argument                      
        self.aacu_rubric_path = aacu_rubric_path      

        self.email = email
        self.password = password
        self.assignment_number = argument.essay
        self.aacu_rubric_data = aacu_rubric_data

        self.provider = None
        self.model_name = None
        self.url = None
 

    #Step 1: get model
    def getllms(self):
        
        self.provider == "chatgpt"
        self.model_name = "gpt-4.1-2025-04-14"

        return ChatOpenAI(model=self.model_name, api_key=os.getenv("OPENAI_API_KEY"))
    
    from browser_use import Agent, ChatOpenAI


    #Step 2: open target website

    def target_website(self, website):
        target_website = {
            "chatgpt": "https://chatgpt.com",
            "gemini": "https://gemini.google.com/app",
            "copilot": "https://copilot.microsoft.com/",
            "claude": "https://claude.ai/login"
        }
        self.url = target_website.get(website, None)

    def prepare_first_prompt(self, first_prompt):

        base_direction = os.path.dirname(os.path.abspath(__file__))
        assignment_prompt_path = os.path.join(base_direction, "assignmentprompt.json")

        with open(assignment_prompt_path, "r", encoding="utf-8") as f:
            first_prompt_data = json.load(f)

        index = self.assignment_number - 1  
        first_prompt = list(first_prompt_data.values())[index]

        self.first_prompt = first_prompt

        print("First Prompt:", first_prompt)

        #sys.exit()


    def prepare_second_prompt(self):

        essay_dir = os.path.join(
            self.base_direction,
            "..",
            f"essay_{self.argument.essay}",
            self.argument.folder
        )

        essay_dir = os.path.abspath(essay_dir)

        #print("AACU", self.aacu_rubric_path)
        #print("essay direction", essay_dir)

        with open(self.aacu_rubric_path, "r", encoding="utf-8") as f:
            aacu_rubric_data = json.load(f)
       
        second_prompt = aacu_rubric_data 

        second_prompt = json.dumps(aacu_rubric_data, indent=2)

        second_prompt = re.sub(r'\s+', ' ', second_prompt.strip().replace("\n", ""))
    
        second_prompt = list(aacu_rubric_data.values())[0]

        print("Second Prompt Length:", second_prompt)

        self.second_prompt = second_prompt

        words = second_prompt.split()

        n = len(words)

        parts = []

        start = 0

        indices = [n * i // 3 for i in range(1, 3)]

        for end in indices + [n]:
            part = " ".join(words[start:end]).replace("\n", "").replace("\r", "")
            parts.append(part)
            start = end

        part1,  part2,  part3 =  parts
        
        return  part1,  part2,  part3
    
    


    #2. Define hyperparameters and paths

    #Step 2: Send prompt  
    def send_prompt(self, website):

        part1,  part2,  part3 = self.prepare_second_prompt()

        followup_prompt = """
        
        Yes, I would like to deliver a fully revised final version of the essay to hit a full 20/20. Also, please explain what changes were made in the essay to reach a perfect 20/20 based on the AAC&U rubric.

        """

        followup_prompt_claude = """
        
        Yes, I would like to deliver a fully revised final version of the 1000-word essay to hit a full 20/20. Also, please explain what changes were made in the essay to reach a perfect 20/20 based on the AAC&U rubric.

        """

        if website == "chatgpt":
            
            prompt = f"""

            1) Go to {self.url} 

            2) Use "Sign in".  

            3) Type Email: {self.email}. Click Next.  

            4) Type password: {self.password}. Click Next. Click Next. 

            5) Wait for 20 seconds for user log in with their security codes. 

            6) Paste the first prompt {self.first_prompt}. Key "Enter" to submit the prompt.  

            7) Wait for 30 seconds for the responses to be generated.  
            
            8) Wait for 10 seconds for the responses to be generated.  

            9) Extract all responses in 30 seconds. 

            10) Extract all responses in 10 seconds.  

            11) Type this prompt, do not enter yet {part1}.  

            12) Type this prompt, do not enter yet {part2}. 

            13) Type this prompt, do not enter yet {part3}.  

            14) Key "Enter" to submit the prompt.  

            15) Wait for 30 seconds for the responses to be generated.  

            16) Wait for 10 seconds for the responses to be generated.  

            17) Extract all responses in 30 seconds. 

            18) Extract all responses in 10 seconds. 

            19) Paste this prompt {followup_prompt}. Key "Enter" to submit the prompt.  

            20) Wait for 30 seconds for the responses to be generated.  
            
            21) Wait for 10 seconds for the responses to be generated. 

            22) Extract all responses in 30 seconds. 

            23) Extract all responses in 10 seconds.

            24) End the session. 


            """

            return prompt
        
        if website == "claude":
            
            prompt = f"""

            Follow this instructions step by step:

            1) Go to {self.url}

            2) Click "Sign in". Use:

                - Email: {self.email} 
                - Password: {self.password}
            
            3) Click Next.

            4) Wait for 20 seconds for user log in with their security codes.

            5) Paste the first prompt {self.first_prompt}. Key "Enter" to submit the prompt. 
            
            6) Wait for 30 seconds for the responses to be generated. 

            7) Wait for 30 seconds for the responses to be generated.
            
            8) Extract all responses in 30 seconds.

            9) Extract all responses in 30 seconds.

            10) Paste this prompt {part1}.
            
            11) Paste this prompt {part2}.
            
            12) Paste this prompt {part3}.

            13) Key "Enter" to submit the prompt. 
            
            14) Wait for 30 seconds for the responses to be generated. 

            15) Wait for 30 seconds for the responses to be generated.
            
            16) Extract all responses in 30 seconds.

            17) Extract all responses in 30 seconds.

            18) Paste this prompt {followup_prompt_claude}. Key "Enter" to submit the prompt.

            19) Wait for 30 seconds for the responses to be generated. 

            20) Wait for 30 seconds for the responses to be generated.
            
            21) Extract all responses in 30 seconds. 

            22) Extract all responses in 30 seconds. 

            23) End the session.

            """

            return prompt
        
 
        if website == "gemini" or website == "copilot":
            
            prompt = f"""

            Follow this instructions step by step:

            1) Go to {self.url}

            2) Click "Sign in".:

                - First, type Email: {self.email}. Key Enter.
                - Then, type Password: {self.password}. Key Enter.
            
            3) Click Next.

            4) Wait for 20 seconds for user log in with their security codes.

            5) Paste the first prompt {self.first_prompt}. Key "Enter" to submit the prompt. 
            
            6) Wait for 30 seconds for the responses to be generated. 

            7) Wait for 30 seconds for the responses to be generated. 
            
            8) Extract all responses in 30 seconds.

            9) Extract all responses in 30 seconds.

            10) Paste this prompt {part1}.

            11) Wait for 5 seconds.
            
            12) Paste this prompt {part2}.

            13) Wait for 5 seconds.

            14) Paste this prompt {part3}.

            15) Wait for 5 seconds.

            16) Key "Enter" to submit the prompt. 
            
            17) Wait for 30 seconds for the responses to be generated. 

            18) Wait for 30 seconds for the responses to be generated.
            
            19) Extract all responses in 30 seconds.

            20) Extract all responses in 30 seconds.

            21) Paste this prompt {followup_prompt}. Key "Enter" to submit the prompt. 

            22) Wait for 30 seconds for the responses to be generated. 

            23) Wait for 30 seconds for the responses to be generated. 
            
            24) Extract all responses in 60 seconds. 

            25) End the session.

            """

            return prompt
        

      #Step 3: run agent

    def agent(self, prompt, interactive=None):

        start_time = time.time()
        
        llm = self.getllms()

        browser = Browser(
            headless=False,
            #executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            #user_data_dir='~/Library/Application Support/Google/Chrome'
            window_size={"width": 1000, "height": 1000},
            )
        
         # Create a permanent output folder
        output_dir = os.path.join(os.getcwd(), "agent_output")
        
        os.makedirs(output_dir, exist_ok=True)

        agent = Agent(task=prompt, llm=llm, browser=browser,  available_file_paths=[output_dir],    
        save_conversation_path=os.path.join(output_dir, "conversation.json"),
        display_files_in_done_text=True,

        )

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

        total_time = time.time() - start_time
        total_minutes = total_time / 60


        print(f"Total time taken: {total_minutes:.2f} minutes")

        save_result_as_json(result, filename="final_result.json", provider=self.provider, essay_number=self.argument.essay)

        return result











    
            



    

