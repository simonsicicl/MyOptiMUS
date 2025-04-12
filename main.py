import os
import json
import traceback
import numpy
from openai import OpenAI
from dotenv import load_dotenv
from template_loader import TemplateLoader

template_path = "./template/"
problem_path = "data/nlp4lp/10/"

if __name__ == "__main__":
    load_dotenv()

    templates = TemplateLoader(template_path=template_path)

    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'), organization=os.environ.get('OPENAI_ORG_KEY'))

    with open(f"{problem_path}/input_targets.json", "r") as f:
        state = json.load(f)
    
    target_type = "constraints"
    model = "gpt-4-1106-preview"
    # model = "gpt-4o"
    seed = 2
    solver = 'gurobipy'
    instruction = templates['formulator_instruction'].format(targetType=target_type)
    state['variables'] = []
    state["objective"] = [state["objective"]]

    print('Formulating...')

    for parameter in state["parameters"]:
        # assert "shape" in parameter.keys(), "shape is not defined for parameter"
        # assert "symbol" in parameter.keys(), "symbol is not defined for parameter"
        # assert (
        #     "definition" in parameter.keys() and len(parameter["definition"]) > 0
        # ), "definition is not defined for parameter"

        if parameter["shape"]:
            code_symbol = parameter["symbol"].split("_")[0]
            parameter["code"] = (
                f'{code_symbol} = np.array(data["{code_symbol}"]) # {parameter["shape"]}'
            )
        else:
            code_symbol = parameter["symbol"].split("_")[0]
            parameter["code"] = (
                f'{code_symbol} = data["{code_symbol}"] # scalar parameter'
            )

    for target in ["constraints", "objective"]:
        state[target] = [
            {
                "description": x,
                "status": "not_formulated",
            }
            for x in state[target]
        ]
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
                {"role": "developer", "content": instruction},
                {"role": "user", "content": prompt},
            ]
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                seed=seed,
            )
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
                {"role": "developer", "content": templates['programmer_variable_instruction'].format(solver=solver)},
                {"role": "user", "content": templates['programmer_variable_prompt'].format(variable=variable)},
            ]
            completion = client.chat.completions.create(messages=messages, model=model, seed=seed)
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
                    {"role": "developer", "content": templates['programmer_' + target_type + '_instruction'].format(solver=solver)},
                    {"role": "user", "content": templates['programmer_' + target_type + '_prompt'].format(context=json.dumps(context, indent=4))},
                ]

                completion = client.chat.completions.create(messages=messages, model=model, seed=seed)
                response = completion.choices[0].message.content
                code = [r.strip() for r in response.split("=====") if len(r.strip()) > 2][0]
                target["code"] = code
                target["status"] = "coded"
            elif target["status"] == "coded":
                pass
    
    # print('state after programming')
    # print(json.dumps(state, indent=4))
    # print("="*20)

    print('Evaluating...')

    local_env = {}
    code = ""
    last_line = ""
    bogus_context = None

    try:
        last_line = templates['prep_code'].format(
            solver_prep_code=templates['solver_prep_code'],
            data_json_path=problem_path+"data.json",
        )
        code += last_line + "\n"

        exec(last_line, local_env, local_env)

        for parameter in state["parameters"]:
            if not "code" in parameter:
                raise Exception(f"Parameter {parameter} is not coded yet!")
            last_line = parameter["code"]
            code += last_line + "\n"
            exec(last_line, local_env, local_env)

        for variable in state["variables"]:
            bogus_context = variable
            last_line = variable["code"]
            code += last_line + "\n"
            exec(last_line, local_env, local_env)

        for constraint in state["constraints"]:
            bogus_context = constraint
            last_line = constraint["code"]
            code += "\n" + last_line + "\n"
            exec(last_line, local_env, local_env)

        bogus_context = state["objective"][0]
        last_line = state["objective"][0]["code"]
        code += "\n" + last_line + "\n"
        exec(last_line, local_env, local_env)

        bogus_context = "OPTIMIZATION CALL"
        last_line = f"\n# Optimize model\nmodel.optimize()\n"
        code += last_line + "\n"
        exec(last_line, local_env, local_env)

        bogus_context = None
        last_line = templates['post_code']
        code += last_line + "\n"
        exec(last_line, local_env, local_env)

        res = {
            "success": True,
            "error_line": None,
            "code": code,
            "obj_val": local_env["obj_val"],
            "status": local_env["status"],
            "error_message": None,
        }
    except Exception as e:
            print("COOOODE")
            print(code)
            print()
            if not bogus_context:
                error_msg = traceback.format_exc()
                raise Exception(
                    f"Unexpected error in running code at {last_line}: "
                    + "\n"
                    + str(e)
                    + "\n\n\n"
                    + error_msg
                )

            error_msg = traceback.format_exc()
            res = {
                "success": False,
                "error_line": last_line,
                "code": code,
                "obj_val": None,
                "status": None,
                "error_message": error_msg,
                "bogus_context": bogus_context,
            }

    if not res["success"]:
        state["solution_status"] = "runtime_error"
        state["error_message"] = res["error_message"]
        state["prep_code"] = templates['prep_code'].format(
            solver_prep_code=templates['solver_prep_code'],
            data_json_path=problem_path+"data.json",
        )

        # if not res["bogus_context"]:
        #     return f"Bad model! Print DONE to finish the execution.", state

        res["bogus_context"]["status"] = "runtime_error"
        state["solver_output_status"] = res["bogus_context"]["status"]

    else:
        state["solution_status"] = "solved"
        state["solver_output_status"] = res["status"]
        state["obj_val"] = res["obj_val"]
        state["code"] = res["code"]
    
    print('state after evaluation')
    print(json.dumps(state, indent=4))
    print("="*20)

