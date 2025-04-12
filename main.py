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

template_path = "./template/"
problem_path = "data/nlp4lp/1/"

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

    with open(f"{problem_path}/input_targets.json", "r") as f:
        state = json.load(f)
    
    state['variables'] = []
    state["objective"] = [state["objective"]]
    state['problem_path'] = problem_path

    print('Formulating...')

    formulator.run(state=state)

    # print('state after formulation')
    # print(json.dumps(state, indent=4))
    # print("="*20)

    print('Programming...')

    programmer.run(state=state)
    
    # print('state after programming')
    # print(json.dumps(state, indent=4))
    # print("="*20)

    print('Evaluating...')

    evaluator.run(state=state)
    
    print('state after evaluation')
    print(json.dumps(state, indent=4))
    print("="*20)

