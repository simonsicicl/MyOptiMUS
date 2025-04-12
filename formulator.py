import json
from openai import OpenAI, Client
from template_loader import TemplateLoader

class Formulator:
    def __init__(self, client:Client, model:str):
        self.client = client
        self.model = model
        self.seed = 2
        self.solver = 'gurobipy'
    def run(self, state:dict, templates:TemplateLoader):
        for parameter in state["parameters"]:
            # assert "shape" in parameter.keys(), "shape is not defined for parameter"
            # assert "symbol" in parameter.keys(), "symbol is not defined for parameter"
            # assert (
            #     "definition" in parameter.keys() and len(parameter["definition"]) > 0
            # ), "definition is not defined for parameter"

            if parameter["shape"]:
                code_symbol = parameter["symbol"].split("_")[0]
                parameter["code"] = (f'{code_symbol} = np.array(data["{code_symbol}"]) # {parameter["shape"]}')
            else:
                code_symbol = parameter["symbol"].split("_")[0]
                parameter["code"] = (f'{code_symbol} = data["{code_symbol}"] # scalar parameter')

        for target in ["constraints", "objective"]:
            state[target] = [{"description": x, "status": "not_formulated"} for x in state[target]]
        for target_type in ['constraints', 'objective']:
            for target in state[target_type]:
                prompt = templates['formulator_prompt'].format(
                    background=state["background"],
                    targetType=target_type,
                    targetDescription=target["description"],
                    variables=json.dumps(
                        [
                            {
                                "definition": v["definition"],
                                "symbol": v["symbol"],
                                "shape": v["shape"],
                            }
                            for v in state["variables"]
                        ],
                        indent=4,
                    ),
                    parameters=json.dumps(
                        [
                            {
                                "definition": p["definition"],
                                "symbol": p["symbol"],
                                "shape": p["shape"],
                            }
                            for p in state["parameters"]
                        ],
                        indent=4,
                    )
                )
                messages = [
                    {"role": "developer", "content": templates['formulator_instruction'].format(targetType=target_type)},
                    {"role": "user", "content": prompt},
                ]
                completion = self.client.chat.completions.create(model=self.model, messages=messages, seed=self.seed)
                output = completion.choices[0].message.content

                output = output[output.find("```json") + 7 :]
                output = output[: output.rfind("```")]
                output = json.loads(output)

                for each in output["auxiliary_constraints"]:
                    state["constraints"].append(each)
                for each in output["new_variables"]:
                    state["variables"].append(each)
                for key_name in output[target_type].keys():
                    target[key_name] = output[target_type][key_name]

        print('state after formulation')
        print(json.dumps(state, indent=4))
        print("="*20)

        print('Programming...')

        for variable in state["variables"]:
            if variable["status"] == "formulated":
                messages = [
                    {"role": "developer", "content": templates['programmer_variable_instruction'].format(solver=self.solver)},
                    {"role": "user", "content": templates['programmer_variable_prompt'].format(variable=variable)},
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
                        {"role": "developer", "content": templates['programmer_' + target_type + '_instruction'].format(solver=self.solver)},
                        {"role": "user", "content": templates['programmer_' + target_type + '_prompt'].format(context=json.dumps(context, indent=4))},
                    ]

                    completion = self.client.chat.completions.create(messages=messages, model=self.model, seed=self.seed)
                    response = completion.choices[0].message.content
                    code = [r.strip() for r in response.split("=====") if len(r.strip()) > 2][0]
                    target["code"] = code
                    target["status"] = "coded"
                elif target["status"] == "coded":
                    pass

        