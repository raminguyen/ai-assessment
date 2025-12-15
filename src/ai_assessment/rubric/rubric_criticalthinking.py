from .rubric import Rubric
import os
import json

class Rubric_CriticalThinking(Rubric):
    def __init__(self):
        super().__init__('critical_thinking')

class Rubric_OralCommunication(Rubric):
    def __init__(self):
        super().__init__('oral_communication')