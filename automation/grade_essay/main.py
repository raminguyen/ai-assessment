from grade import *
from browser_use import Browser, Agent, ChatOpenAI
from dotenv import load_dotenv
import os, json
import argparse
import sys
import re

#1: Load email and password.

load_dotenv()

EMAIL = os.getenv("EMAIL")

PASSWORD  = os.getenv("PASS")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-e",
        "--essay",
        required=True,
        help="source model (chatgpt, gemini, claude, copilot)",
    )

    parser.add_argument(
        "-a",
        "--assignment",
        required=True,
        type=int,
        help="assignment number",
    )

    parser.add_argument(
        "-grade",
        "--grade_model",
        required=True,
        help="grading model (chatgpt, gemini, claude, copilot)",
    )

    args = parser.parse_args()

    grader = EssayGrader(
        essay=args.essay,
        assignment=args.assignment,
        model_grade=args.grade_model,
        email=EMAIL,
        password=PASSWORD

    )

    grader.target_website()
    grader.load_tuned_essay()
    grader.load_rubric()
    grader.send_prompt()
    grader.agent()