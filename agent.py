import json
from openai import OpenAI, Client
from template_loader import TemplateLoader

class Agent:
    def __init__(self, name:str, description:str, client:Client, model:str, templates:TemplateLoader):
        self.name=name
        self.description=description
        self.client = client
        self.model = model
        self.seed = 2
        self.solver = 'gurobipy'
        self.templates = templates

    def run(self, state:dict) -> tuple[str, dict]: 
        print('Basic agent, no run code!')