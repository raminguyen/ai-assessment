from test import Rubric, Essay, Model, ModelGemini3ProPreview
from test import Util
import os
import sys
api_key = os.getenv("GOOGLE_API_KEY")

#1: Create an instance 

model = ModelGemini3ProPreview()

essay = Essay("My First Essay")

rubric = Rubric("critical_thinking")

#1. Load a prompt
essay.load_prompt()

print(essay.grade_prompt)

#
#
#

#2. assignment prompt
print(essay.load_essay())

result = model.tune(essay, rubric)

print(result)

Util.texttojson(result, "output.json")

Util.jsontodoc(json="output.json")


"""#1: Create an instance 

model = ModelGemini3ProPreview()

essay = Essay("My First Essay")

rubric = None

#2. assignment prompt
essay.prompt()

result = model.generate(essay, rubric)

print(result)

"""
