from test import Rubric, Essay, Model, ModelGemini3ProPreview
import os
import sys
api_key = os.getenv("GOOGLE_API_KEY")



#1: Create an instance 

model = ModelGemini3ProPreview()

essay = Essay("My First Essay")

rubric = None

#1. Load a prompt
essay.load_prompt()

print(essay.grade_prompt)

sys.exit()

#2. assignment prompt
essay.load_essay()

result = model.tune(essay, rubric)

print(result)


"""#1: Create an instance 

model = ModelGemini3ProPreview()

essay = Essay("My First Essay")

rubric = None

#2. assignment prompt
essay.prompt()

result = model.generate(essay, rubric)

print(result)

"""
