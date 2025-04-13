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
        try:
            if state["solution_status"] == "runtime_error":
                return self._debug(state=state)
            elif state['solution_status'] == None:
                return self._gen_code(state=state)
            else:
                return ("CRASHED", state)
        except:
            return ("CRASHED", state)
    
    def _gen_code(self, state:dict) -> tuple[str, dict]: 
        if not "variables" in state.keys():
            return ("CRASHED", state)
        for variable in state["variables"]:
            if not "status" in variable.keys():
                return ("CRASHED", state)
            if variable["status"] == "formulated":
                try:
                    messages = [
                        {"role": "developer", "content": self.templates['programmer_variable_instruction'].format(solver=self.solver)},
                        {"role": "user", "content": self.templates['programmer_variable_prompt'].format(variable=variable)},
                    ]
                except:
                    return ("CRASHED", state)
                for cnt in range(2, -2, -1):
                    # assert cnt >= 0, "    Programmer : Generating code for got variable invalid response!"
                    if cnt < 0:
                        return ("CRASHED", state)
                    try:
                        completion = self.client.chat.completions.create(messages=messages, model=self.model, seed=cnt)
                        response = completion.choices[0].message.content
                        code = [r.strip() for r in response.split("=====") if len(r.strip()) > 2][0]
                        break
                    except Exception as e:
                        print("    Programmer : Generating code for variable got invalid response! Try again ...")
                variable["code"] = code
                variable["status"] = "coded"
            elif variable["status"] == "coded":
                pass

        for target_type in ["constraints", "objective"]:
            if not target_type in state.keys():
                return ("CRASHED", state)
            for target in state[target_type]:
                if not "status" in target.keys():
                    return ("CRASHED", state)
                if target["status"] == "formulated":
                    try:
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
                    except:
                        return ("CRASHED", state)
                    for cnt in range(2, -2, -1):
                        # assert cnt >= 0, "    Programmer : Generating code for {target_type} got invalid response!".format(target_type=target_type)
                        if cnt < 0:
                            return ("CRASHED", state)
                        try:
                            completion = self.client.chat.completions.create(messages=messages, model=self.model, seed=cnt)
                            response = completion.choices[0].message.content
                            code = [r.strip() for r in response.split("=====") if len(r.strip()) > 2][0]
                            break
                        except Exception as e:
                            print("    Programmer : Generating code for {target_type} got invalid response! Try again ...").format(target_type=target_type)
                    target["code"] = code
                    target["status"] = "coded"
                elif target["status"] == "coded":
                    pass
        return "Programming Done!", state
    
    def _debug(self, state:dict) -> tuple[str, dict]: 
        error_line = None
        bogus_context = None
        try:
            for target in ["constraints", "objective", "variables"]:
                for item in state[target]:
                    if item["status"] == "runtime_error":
                        bogus_context = item
        except:
            return ("CRASHED", state)
            
        if not bogus_context:
            return ("CRASHED", state)
            # raise Exception("No runtime error in state!", json.dumps(state, indent=4))

        try:
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
                        if not "code" in variable.keys():
                            return ("CRASHED", state)
                            # raise Exception(f"Variable {variable} is not coded yet!")
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
                return ("CRASHED", state)
                # raise Exception(f"Invalid bogus_context {bogus_context}! \n {json.dumps(state, indent=4)}")
        except:
            return ("CRASHED", state)
        
        for cnt in range(2, -2, -1):
            # assert cnt >= 0, "    Programmer : Debug got invalid response!"
            if cnt < 0:
                return ("CRASHED", state)
            try:
                completion = self.client.chat.completions.create(messages=messages, model=self.model, seed=cnt)
                response = completion.choices[0].message.content
                response = response.split("```json")[1].split("```")[0]
                update = json.loads(response)
                break
            except Exception as e:
                print("    Programmer : Debug got invalid response! Try again ...")
        
        try:
            if update["status"] == "correct":
                bogus_context["status"] = "formulation_error"
                return update["reason"], state
            elif update["status"] == "fixed":
                bogus_context["status"] = "coded"
                bogus_context["code"] = update["fixed_code"]
                return "The code is fixed! Try evaluating it again.", state
            else:
                return ("CRASHED", state)
                # raise Exception(f"Invalid status {update['status']}!")
        except:
            return ("CRASHED", state)