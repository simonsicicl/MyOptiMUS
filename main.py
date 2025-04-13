import os
import json
import traceback
import numpy
from openai import OpenAI
from dotenv import load_dotenv
from template_loader import TemplateLoader
from formulator import Formulator
from programmer import Programmer
from evaluator import Evaluator
from manager import Manager

template_path = "./template/"
problem_path = "data/nlp4lp/10/"
log_path = 'log/'

model = "gpt-4-1106-preview"
# model = "gpt-4o"
seed = 2
solver = 'gurobipy'

if __name__ == "__main__":
    load_dotenv()

    templates = TemplateLoader(template_path=template_path)
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'), organization=os.environ.get('OPENAI_ORG_KEY'))

    formulator = Formulator(client=client, model=model, templates=templates)
    programmer = Programmer(client=client, model=model, templates=templates)
    evaluator = Evaluator(client=client, model=model, templates=templates)
    manager = Manager(client=client, model=model, templates=templates, agents=[formulator, programmer, evaluator])

    with open(f"{problem_path}/input_targets.json", "r") as f:
        state = json.load(f)
    
    state['variables'] = []
    state["objective"] = [state["objective"]]
    state['problem_path'] = problem_path
    state['log_path'] = log_path
    state["solution_status"] = None

    manager.run(state=state)

    # print('Formulating...')

    # (message, state) = formulator.run(state=state)
    # print(message)

    # print('state after formulation')
    # print(json.dumps(state, indent=4))
    # print("="*20)

    # print('Programming...')

    # (message, state) = programmer.run(state=state)
    # print(message)
    
    # print('state after programming')
    # print(json.dumps(state, indent=4))
    # print("="*20)

    # print('Evaluating...')

    # (message, state) = evaluator.run(state=state)
    # print(message)
    
    # print('state after evaluation')
    # print(json.dumps(state, indent=4))
    # print("="*20)

