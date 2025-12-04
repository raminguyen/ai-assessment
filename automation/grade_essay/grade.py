import os 
from browser_use import Browser, Agent, ChatOpenAI
import json 
import time
import asyncio


class EssayGrader:
    def __init__(self, essay=None, assignment=None, email=None, password=None, model_grade=None):
        
        self.essay = essay             # chatgpt, gemini, claude, copilot
        self.assignment = assignment      # essay number (int)
        self.email = email                # login email
        self.password = password          # login password
        self.model_grade = model_grade    # grade with (gemini, chatgpt, claude, copilot)
        self.url = None                   # website url
        self.essay_text = None            # tuned essay you feed in
        self.prompt_text = None           # prompt to evaluate
        self.provider = None
        

    def target_website(self):
        websites = {
            "chatgpt": "https://chatgpt.com",
            "gemini": "https://gemini.google.com/app",
            "copilot": "https://copilot.microsoft.com/",
            "claude": "https://claude.ai/login"
        }
        self.url = websites.get(self.model_grade)

    def load_tuned_essay(self):

        base_dir = os.getcwd()

        folder = f"tuned_essay{self.assignment}"

        file_name = {
            "chatgpt": "chatgpt.json",
            "gemini": "gemini.json",
            "claude": "claudeai.json",
            "copilot": "copilot.json"
        }.get(self.essay)

        full_path = os.path.join(base_dir, folder, file_name)

        with open(full_path, 'r') as file:
            data = json.load(file)

        self.essay_text = data['content']

    def load_rubric(self):

        base_dir = os.getcwd()

        json_path = os.path.join(base_dir, "..", "essay_generation", "aacu_rubrics.json")

        with open(json_path, 'r') as file:
            data = json.load(file)
       
        self.rubric_data = data["critical_thinking"]

    def getllms(self):
        self.provider = "chatgpt"
        model_name = "gpt-4.1-2025-04-14"
        return ChatOpenAI(model=model_name, api_key=os.getenv("OPENAI_API_KEY"))
    
    def send_prompt(self):
        essay_text = self.essay_text

        rubric_text = self.rubric_data

        combined_text = f"{essay_text} {rubric_text}"

        combined_text = " ".join(combined_text.split())

        words = combined_text.split()

        n = len(words)
        print(n)
        #import sys

        #sys.exit()

        cuts = [n * i // 10 for i in range(1, 10)]

        part1  = " ".join(words[:cuts[0]])
        part2  = " ".join(words[cuts[0]:cuts[1]])
        part3  = " ".join(words[cuts[1]:cuts[2]])
        part4  = " ".join(words[cuts[2]:cuts[3]])
        part5  = " ".join(words[cuts[3]:cuts[4]])
        part6  = " ".join(words[cuts[4]:cuts[5]])
        part7  = " ".join(words[cuts[5]:cuts[6]])
        part8  = " ".join(words[cuts[6]:cuts[7]])
        part9  = " ".join(words[cuts[7]:cuts[8]])
        part10 = " ".join(words[cuts[8]:])

        if self.model_grade == "chatgpt":
            prompt = f""" Follow step by step
                1) Go to {self.url}
                2) Type the prompt: good morning.
                3) Key "Enter" to submit the prompt.
                4) Extract all responses
                5) End the session."""
            self.agent_prompt = prompt

            return prompt
        

        elif self.model_grade == "claude":
        
            prompt = f""" Follow step by step

            1) Go to {self.url} 

                2) Click Sign In.

                3) Type Email: {self.email}.

                4) Type Password: {self.password}.

                5) Click Next.

                6) Wait for 10 seconds for user log in with their security codes. 

                7) Type this prompt, do not enter yet {part1}.  

                8) Type this prompt, do not enter yet {part2}. 

                9) Type this prompt, do not enter yet {part3}.  

                10) Type this prompt, do not enter yet {part4}.  

                11) Type this prompt, do not enter yet {part5}.  

                12) Type this prompt, do not enter yet {part6}.

                13) Type this prompt, do not enter yet {part7}.

                14) Type this prompt, do not enter yet {part8}.

                15) Type this prompt, do not enter yet {part9}.

                16) Type this prompt, do not enter yet {part10}.

                17) Key "Enter" to submit the prompt.

                18) Wait for 30 seconds for the responses to be generated.  

                19) Wait for 10 seconds for the responses to be generated.

                20) Extract all responses in 30 seconds.

                21) Extract all responses in 10 seconds.

                22) End the session.

        """
            self.agent_prompt = prompt
        
            return prompt
    
    def save_result(self, result):

        serializable = [
            r.model_dump(exclude_none=True) if hasattr(r, "model_dump") else str(r)
            for r in result
        ]

        assignment_id = self.assignment
        save_dir = os.path.join("grade", f"tuned_essay{assignment_id}")

        # new readable file name
        file_name = f"{self.model_grade}_grade_{self.essay}.json"
        save_path = os.path.join(save_dir, file_name)

        os.makedirs(save_dir, exist_ok=True)

        with open(save_path, "w") as f:
            json.dump({"result": serializable}, f, indent=4)

        print(f"Saved final result to: {save_path}")

    def agent(self):

        start_time = time.time()

        llm = self.getllms()

        browser = Browser(
            headless=False
        )

        agent = Agent(
            task = self.agent_prompt, 
            llm=llm,
            browser=browser
        )

        end_time = time.time()

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

        self.save_result(result)

        end_time = time.time()
        total_time = end_time - start_time

        print(f"Total time: {total_time:.2f} seconds")





