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
# model = "gpt-4o"
solver = 'gurobipy'

if __name__ == "__main__":
    load_dotenv()
    gp.Model()

    templates = TemplateLoader(template_path=template_path)
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'), organization=os.environ.get('OPENAI_ORG_KEY'))

    formulator = Formulator(client=client, model=model, templates=templates)
    programmer = Programmer(client=client, model=model, templates=templates)
    evaluator = Evaluator(client=client, model=model, templates=templates)

    manager = Manager(client=client, model=model, templates=templates, agents=[formulator, programmer, evaluator])
    dataset = "complexor"
    problem = "AircraftAssignment"
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
    
    manager.run(state=state)

