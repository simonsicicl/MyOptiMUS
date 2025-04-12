import json
from openai import OpenAI, Client
from template_loader import TemplateLoader

class Agent:
    def __init__(self, client:Client, model:str, templates:TemplateLoader):
        self.client = client
        self.model = model
        self.seed = 2
        self.solver = 'gurobipy'
        self.templates = templates

    def run(self, state:dict):
        print('Basic agent, no run code!')