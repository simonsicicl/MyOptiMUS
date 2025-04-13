import json
from openai import OpenAI, Client
from template_loader import TemplateLoader
from agent import Agent

class Formulator(Agent):
    def __init__(self, client:Client, model:str, templates:TemplateLoader):
        super().__init__(
            name="Formulator",
            description="This is a mathematical formulator agent that is an expert in mathematical and optimization modeling and can define and modify variables, constraints, and objective functions. Does 3 things: 1) Defining constraints, variables, and objective functions, 2) Modifying constraints, variables, and objective functions, 3) Other things related to mathematical formulation. If the history is empty, start from this agent.",
            client=client, model=model, templates=templates
            )

    def run(self, state:dict) -> tuple[str, dict]: 
        for target_type in ['constraints', 'objective']:
            for target in state[target_type]:
                if not "status" in target.keys():
                    return ("CRASHED", state)
                
                if target["status"] == "formulated" or target["status"] == "coded":
                    continue

                if target["status"] == "runtime_error":
                    try:
                        prompt = self.templates['formulator_fix_prompt'].format(
                            target=target_type,
                            constraint=json.dumps(target["description"], indent=4),
                            variables=json.dumps(state["variables"], indent=4),
                            parameters=json.dumps(state["parameters"], indent=4),
                            formulation=json.dumps(target["formulation"], indent=4),
                            json=json.dumps(target),
                            error=state["error_message"],
                        )
                        messages = [
                            {"role": "developer", "content": self.templates['formulator_fix_instruction'].format(target=target_type)},
                            {"role": "user", "content": prompt}
                        ]
                    except:
                        return ("CRASHED", state)
                    for cnt in range(2, -2, -1):
                        # assert cnt >= 0, "    Invalid json format!"
                        if cnt < 0:
                            return ("CRASHED", state)
                        try:
                            completion = self.client.chat.completions.create(model=self.model, messages=messages, seed=cnt)
                            output = completion.choices[0].message.content
                            output = output[output.find("```json") + 7 :]
                            
                            output = output[: output.rfind("```")]
                            update = json.loads(output)

                            break
                        except Exception as e:
                            print(f"    Invalid json format in {target_type} formulation! Try again ...")
                    try:
                        target["formulation"] = update["formulation"]
                        target["related_variables"] = update["related_variables"]
                        target["related_parameters"] = update["related_parameters"]
                        target["status"] = "formulated"
                        return "Formulation Done!", state
                    except:
                        return ("CRASHED", state)
                
                # assert target["status"] == "not_formulated", f"Invalid status: {json.dumps(target, indent=4)}"
                if target["status"] != "not_formulated":
                    return ("CRASHED", state)
                try:
                    prompt = self.templates['formulator_prompt'].format(
                        background=state["background"],
                        targetType=target_type,
                        targetDescription=target["description"],
                        variables=json.dumps(state["variables"], indent=4),
                        parameters=json.dumps(state["parameters"], indent=4)
                    )
                    messages = [
                        {"role": "developer", "content": self.templates['formulator_instruction'].format(targetType=target_type)},
                        {"role": "user", "content": prompt},
                    ]
                except:
                    return ("CRASHED", state)
                for cnt in range(2, -2, -1):
                    # assert cnt >= 0, "    Invalid json format!"
                    if cnt < 0:
                        return ("CRASHED", state)
                    try:
                        completion = self.client.chat.completions.create(model=self.model, messages=messages, seed=cnt)
                        output = completion.choices[0].message.content
                        output = output.split("```json")[1].split("```")[0]
                        output = json.loads(output)

                        for each in output["auxiliary_constraints"]:
                            state["constraints"].append(each)
                        for each in output["new_variables"]:
                            state["variables"].append(each)
                        for key_name in output[target_type].keys():
                            target[key_name] = output[target_type][key_name]
                        break
                    except Exception as e:
                        print(f"    Invalid json format in {target_type} formulation! Try again ...")
        return "Formulation Done!", state