import json
from openai import OpenAI, Client
from template_loader import TemplateLoader
from agent import Agent

class Programmer(Agent):
    def __init__(self, client:Client, model:str, templates:TemplateLoader):
        super().__init__(
            name="Programmer",
            description="This is a mathematical programmer agent that is an expert in writing, modifying, and debugging code for optimization problems from the mathematical formulation of the problem. This agent should be called first when a bug or error happens in the code.",
            client=client, model=model, templates=templates
            )

    def run(self, state:dict) -> tuple[str, dict]: 
        for variable in state["variables"]:
            if variable["status"] == "formulated":
                messages = [
                    {"role": "developer", "content": self.templates['programmer_variable_instruction'].format(solver=self.solver)},
                    {"role": "user", "content": self.templates['programmer_variable_prompt'].format(variable=variable)},
                ]
                completion = self.client.chat.completions.create(messages=messages, model=self.model, seed=self.seed)
                response = completion.choices[0].message.content
                code = [r.strip() for r in response.split("=====") if len(r.strip()) > 2][0]
                variable["code"] = code
                variable["status"] = "coded"
            elif variable["status"] == "coded":
                pass

        for target_type in ["constraints", "objective"]:
            for target in state[target_type]:
                if target["status"] == "formulated":
                    context = {}
                    context["description"] = target["description"]
                    context["formulation"] = target["formulation"]
                    context["related_variables"] = []
                    context["related_parameters"] = []

                    for each in state["parameters"]:
                        if each["symbol"] in target["related_parameters"]:
                            context["related_parameters"].append(each)

                    for each in state["variables"]:
                        if each["symbol"] in target["related_variables"]:
                            context["related_variables"].append(each)

                    messages = [
                        {"role": "developer", "content": self.templates['programmer_' + target_type + '_instruction'].format(solver=self.solver)},
                        {"role": "user", "content": self.templates['programmer_' + target_type + '_prompt'].format(context=json.dumps(context, indent=4))},
                    ]

                    completion = self.client.chat.completions.create(messages=messages, model=self.model, seed=self.seed)
                    response = completion.choices[0].message.content
                    code = [r.strip() for r in response.split("=====") if len(r.strip()) > 2][0]
                    target["code"] = code
                    target["status"] = "coded"
                elif target["status"] == "coded":
                    pass
        return "Programming Done!", state