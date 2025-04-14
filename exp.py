import os
import json
import traceback
import numpy
import gurobipy as gp
import time
from openai import OpenAI
from dotenv import load_dotenv
from template_loader import TemplateLoader
from formulator import Formulator
from programmer import Programmer
from evaluator import Evaluator
from manager import Manager

template_path = "./template/"
model = "gpt-4-1106-preview"
dataset = "nl4opt"
max_rounds = 10

if __name__ == "__main__":
    load_dotenv(verbose=True, override=True)
    gp.Model()

    templates = TemplateLoader(template_path=template_path)
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'), organization=os.environ.get('OPENAI_ORG_KEY'))

    formulator = Formulator(client=client, model=model, templates=templates)
    programmer = Programmer(client=client, model=model, templates=templates)
    evaluator = Evaluator(client=client, model=model, templates=templates)
    if os.path.exists(f'logs/{dataset}_{model}.json'):
        with open(f'logs/{dataset}_{model}.json', 'r') as f:
            exp_record = json.load(f)
    else:
        exp_record = {
            "problems": [], 
            "calls_count": {}, 
            "agent_calls": {"Formulator": 0, "Programmer": 0, "Evaluator": 0}, 
            "total_solved": 0, 
            "total_problems": len(os.listdir(f"data/{dataset}/"))
        }
        for i in range(3, max_rounds+1):
            exp_record["calls_count"][f'{i}'] = 0
    exist = [each['problem'] for each in exp_record['problems']]

    for problem in os.listdir(f"data/{dataset}/"):
        if problem in exist:
            continue
        exist.append(problem)
        print(f'***Solving problem {problem}...')
        manager = Manager(client=client, model=model, templates=templates, agents=[formulator, programmer, evaluator], max_rounds=max_rounds)
        problem_path = f"data/{dataset}/{problem}/"
        log_path = f"logs/log_{time.strftime('%Y%m%d%H%M%S')}_{dataset}_{problem}/"

        if not os.path.exists(log_path):
            os.makedirs(log_path)

        with open(f"{problem_path}/input_targets.json", "r") as f:
            state = json.load(f)

        state = {
            "background": state["background"],
            "problem_type": "LP",
            "parameters": state["parameters"],
            "constraints": state["constraints"],
            "variables": [],
            "objective": [state["objective"]],
            "solution_status": None,
            "solver_output_status": None,
            "error_message": None,
            "obj_val": None,
            "log_path": log_path,
            "problem_path": problem_path,
        }
        
        message, state = manager.run(state=state)

        if message == "The problem is solved.":
            exp_record["problems"].append({
                "problem": problem,
                "status": "solved",
                "round": state['round'],
                "agent_calls": state['agent_calls']
            })
            exp_record["calls_count"][f'{state['round']}'] += 1
            for agent_name in exp_record["agent_calls"].keys():
                exp_record["agent_calls"][agent_name] += state["agent_calls"][agent_name]
            exp_record["total_solved"] += 1
        else:
            exp_record["problems"].append({
                "problem": problem,
                "status": "failed",
            })
        
        with open(f'logs/{dataset}_{model}.json', 'w') as f:
            json.dump(exp_record, f, indent=4)


