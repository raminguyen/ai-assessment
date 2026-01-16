import argparse
from datetime import datetime
from ai_assessment import Runner
import os 

def main():

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    
    gen = subparsers.add_parser('generate')
    gen.add_argument('model', choices=['chatgpt', 'gemini', 'claude', 'grok'])
    gen.add_argument('assignment', type=int)
    gen.add_argument('--folder', type=str, required=True, help='Folder name for rubric')
    gen.add_argument('--prompt', type=int, default=1, help='Prompt number (1 or 2)')

    tune = subparsers.add_parser('tune')
    tune.add_argument('model', choices=['chatgpt', 'gemini', 'claude', 'grok'])
    tune.add_argument('assignment', type=int)
    tune.add_argument('rubric', type=str)
    tune.add_argument('--prompt', type=int, default=1, help='Prompt number (1 or 2)')

    score = subparsers.add_parser('score')
    score.add_argument('grader', choices=['chatgpt', 'gemini', 'claude', 'grok'])
    score.add_argument('rubric', type=str)
    score.add_argument('filename', help='Individual file to read')
    score.add_argument('assignment', type=int)
    score.add_argument('--prompt', type=int, default=1, help='Prompt number (1 or 2)')

    reflect = subparsers.add_parser('reflection')
    reflect.add_argument('model', choices=['chatgpt', 'gemini', 'claude', 'grok'])
    reflect.add_argument('assignment', type=int)
    reflect.add_argument('rubric', type=str)
    reflect.add_argument('--prompt', type=int, default=1, help='Prompt number (1 or 2)')

    args = parser.parse_args()

    runner = Runner()

    if args.command == 'generate':
        runner.generate(args.model, args.assignment, args.folder, args.prompt)

    elif args.command == 'tune':
        runner.tune(args.model, args.assignment, args.rubric, args.prompt)

    elif args.command == 'score':
        runner.score(args.grader, args.rubric, args.filename, args.assignment, args.prompt)

    elif args.command == 'reflection':
        runner.reflect(args.model, args.assignment, args.rubric, args.prompt)


if __name__ == "__main__":
    main()

