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
        if state["solution_status"] == "runtime_error":
            return self._debug(state=state)
        elif state['solution_status'] == None:
            return self._gen_code(state=state)
        else:
            raise Exception(f"Invalid solver_output_status {state['solver_output_status']}!")
    
    def _gen_code(self, state:dict) -> tuple[str, dict]: 
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
    
    def _debug(self, state:dict) -> tuple[str, dict]: 
        error_line = None
        bogus_context = None

        for target in ["constraints", "objective", "variables"]:
            for item in state[target]:
                if item["status"] == "runtime_error":
                    bogus_context = item
            
        if not bogus_context:
            raise Exception("No runtime error in state!", json.dumps(state, indent=4))

        context = {}
        prep_code = state["prep_code"]

        if "description" in bogus_context:
            error_line = bogus_context["code"]
            error_message = state["error_message"]
            for parameter in state["parameters"]:
                if parameter["symbol"] in bogus_context["related_parameters"]:
                    prep_code += parameter["code"] + "\n"

            for variable in state["variables"]:
                if variable["symbol"] in bogus_context["related_variables"]:
                    if not "code" in variable:
                        raise Exception(f"Variable {variable} is not coded yet!")

                    prep_code += variable["code"] + "\n"
            prompt = self.templates['programmer_debuger_targets_prompt'].format(
                target=target,
                prep_code=prep_code,
                error_line=error_line,
                error_message=error_message,
            )
            messages = [
                {"role": "developer", "content": self.templates['programmer_debuger_targets_instruction']},
                {"role": "user", "content": prompt},
            ]

        elif "definition" in bogus_context:
            
            error_line = bogus_context["code"]
            error_message = state["error_message"]

            prompt = self.templates['programmer_debuger_variable_prompt'].format(
                target=target,
                prep_code=prep_code,
                error_line=error_line,
                error_message=error_message,
            )
            messages = [
                {"role": "developer", "content": self.templates['programmer_debuger_variable_instruction']},
                {"role": "user", "content": prompt},
            ]

        else:
            raise Exception(
                f"Invalid bogus_context {bogus_context}! \n {json.dumps(state, indent=4)}"
            )

        completion = self.client.chat.completions.create(messages=messages, model=self.model, seed=self.seed)
        response = completion.choices[0].message.content

        response = response.split("```json")[1].split("```")[0]
        print(response)
        input()

        update = json.loads(response)

        if update["status"] == "correct":
            bogus_context["status"] = "formulation_error"
            return update["reason"], state
        elif update["status"] == "fixed":
            bogus_context["status"] = "coded"
            bogus_context["code"] = update["fixed_code"]
            return "The code is fixed! Try evaluating it again.", state
        else:
            raise Exception(f"Invalid status {update['status']}!")