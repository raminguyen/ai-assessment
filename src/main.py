import argparse
from datetime import datetime
from ai_assessment import Run
import os 

def main():

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    
    gen = subparsers.add_parser('generate')
    gen.add_argument('model', choices=['chatgpt', 'gemini', 'claude', 'grok'])
    gen.add_argument('assignment', type=int)
    gen.add_argument('--folder', type=str, required=True, help='Folder name for rubric')

    tune = subparsers.add_parser('tune')
    tune.add_argument('model', choices=['chatgpt', 'gemini', 'claude', 'grok'])
    tune.add_argument('assignment', type=int)
    tune.add_argument('rubric', type=str)
    
    score = subparsers.add_parser('score')
    score.add_argument('grader', choices=['chatgpt', 'gemini', 'claude', 'grok'])
    score.add_argument('rubric', type=str)
    score.add_argument('filename', help='Individual file to read')
    score.add_argument('assignment', type=int)


    args = parser.parse_args()
    Runner = Run()

    Runner.run(args)

if __name__ == "__main__":
    main()