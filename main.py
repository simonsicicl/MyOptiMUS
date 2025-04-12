import os
import json
from openai import OpenAI
from dotenv import load_dotenv

manager_promt_template = """
        
You're a manager in a team of optimization experts. The goal of the team is to solve an optimization problem. Your task is to choose the next expert to work on the problem based on the current situation. 
- The user has already given us the problem description, the objective function, and the parameters. Only call the user proxy if there is a problem or something ambiguous or missing. 

Here's the list of agents in your team:
-----
{agents}
-----

And here's the history of the conversation so far:
-----
{history}
-----


Considering the history, if you think the problem is solved, type DONE. Otherwise, generate a json file with the following format:
{{
    "agent_name": "Name of the agent you want to call next",
    "task": "The task you want the agent to carry out"
}}

to identify the next agent to work on the problem, and also the task it has to carry out. 
- If there is a runtime error, ask the the prorammer agent to fix it.
- Only generate the json file, and don't generate any other text.
- If the latest message in history says that the code is fixed, ask the evaluator agent to evaluate the code!

"""

formulator_instruction_template = """
You are an expert mathematical formulator and an optimization professor at a top university. Your task is to model {targetType} of the problem in the standard LP or MILP form. 
"""

# formulator_prompt_template = """

# Here is a {targetType} we need you to model:
# -----
# {targetDescription}
# -----

# Here is some context on the problem:
# -----
# {background}
# -----

# Here is the list of available variables:
# -----
# {variables}
# -----

# And finally, here is list of input parameters:
# -----
# {parameters}
# -----

# First, take a deep breath and explain how we should define the {targetType}. Feel free to define new variables if you think it is necessary. Then, generate a json file accordingly with the following format (STICK TO THIS FORMAT!):


# {{
#     "{targetType}": {{
#       "description": "The description of the {targetType}",
#       "formulation": "The LaTeX mathematical expression representing the formulation of the {targetType}"
#     }},
#     "auxiliary_constraints": [
#         {{
#             "description": "The description of the auxiliary constraint",
#             "formulation": "The LaTeX mathematical expression representing the formulation of the auxiliary constraint"
#         }}
#     ]
#     "new_variables": [
#         {{
#             "definition": "The definition of the variable",
#             "symbol": "The symbol for the variable",
#             "shape": [ "symbol1", "symbol2", ... ]
#         }}
#     ],
#     "related_variables": [
#         {{

#         }}
#     ]
# }}

# - Your formulation should be in LaTeX mathematical format (do not include the $ symbols). 
# - Note that I'm going to use python json.loads() function to parse the json file, so please make sure the format is correct (don't add ',' before enclosing '}}' or ']' characters.
# - Generate the complete json file and don't omit anything.
# - Use '```json' and '```' to enclose the json file.
# - Important: You can not define new parameters. You can only define new variables.Use CamelCase and full words for new variable symbols, and do not include indices in the symbol (e.g. ItemsSold instead of itemsSold or items_sold or ItemsSold_i)
# - Use \\textup{{}} when writing variable and parameter names. For example (\\sum_{{i=1}}^{{N}} \\textup{{ItemsSold}}_{{i}} instead of \\sum_{{i=1}}^{{N}} ItemsSold_{{i}})
# - Use \\quad for spaces.
# - Use empty list ([]) if no new variables are defined.
# - Always use non-strict inequalities (e.g. \\leq instead of <), even if the constraint is strict.
# - Define auxiliary constraints when necessary. Set it to an empty list ([]) if no auxiliary constraints are needed. If new auxiliary constraints need new variables, add them to the "new_variables" list too.
# - All \\ in the result should be expended to \\\\ to fit the format string requirement, included the term mentioned before

# Take a deep breath and solve the problem step by step.

# """

formulator_prompt_template = """

Here is a {targetType} we need you to model:
-----
{targetDescription}
-----

Here is some context on the problem:
-----
{background}
-----

Here is the list of available variables:
-----
{variables}
-----

And finally, here is list of input parameters:
-----
{parameters}
-----

First, take a deep breath and explain how we should define the {targetType}. Feel free to define new variables if you think it is necessary. Then, generate a json file accordingly with the following format (STICK TO THIS FORMAT!):


{{
    "{targetType}": {{
        "description": "The description of the {targetType}",
        "status": "formulated",
        "formulation": "The LaTeX mathematical expression representing the formulation of the {targetType}",
        "related_variables": [ "variable1", "variable2", ...],
        "related_parameters" : [ "parameter1", "parameter2", ...]
    }},
    "auxiliary_constraints": [
        {{
            "description": "The description of the auxiliary constraint",
            "status": "formulated",
            "formulation": "The LaTeX mathematical expression representing the formulation of the auxiliary constraint"
            "related_variables": [ "variable1", "variable2", ...],
            "related_parameters" : [ "parameter1", "parameter2", ...]
        }}
    ]
    "new_variables": [
        {{
            "definition": "The definition of the variable",
            "symbol": "The symbol for the variable",
            "shape": [ "symbol1", "symbol2", ... ],
            "status": "formulated"
        }}
    ]
}}

- Your formulation should be in LaTeX mathematical format (do not include the $ symbols). 
- Note that I'm going to use python json.loads() function to parse the json file, so please make sure the format is correct (don't add ',' before enclosing '}}' or ']' characters.
- Generate the complete json file and don't omit anything.
- Use '```json' and '```' to enclose the json file.
- Important: You can not define new parameters. You can only define new variables.Use CamelCase and full words for new variable symbols, and do not include indices in the symbol (e.g. ItemsSold instead of itemsSold or items_sold or ItemsSold_i)
- Use \\textup{{}} when writing variable and parameter names. For example (\\sum_{{i=1}}^{{N}} \\textup{{ItemsSold}}_{{i}} instead of \\sum_{{i=1}}^{{N}} ItemsSold_{{i}})
- Use \\quad for spaces.
- Use empty list ([]) if no new variables are defined.
- Always use non-strict inequalities (e.g. \\leq instead of <), even if the constraint is strict.
- Define auxiliary constraints when necessary. Set it to an empty list ([]) if no auxiliary constraints are needed. If new auxiliary constraints need new variables, add them to the "new_variables" list too.
- All \\ in the result should be expended to \\\\ to fit the format string requirement, included the term mentioned before

Take a deep breath and solve the problem step by step.

"""

problem_path = "data/nlp4lp/1/"




if __name__ == "__main__":
    load_dotenv()

    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'), organization=os.environ.get('OPENAI_ORG_KEY'))

    with open(f"{problem_path}/input_targets.json", "r") as f:
        state = json.load(f)
    
    target_type = "constraints"
    model = "gpt-4-1106-preview"
    seed = 2
    # model = "gpt-4o"
    instruction = formulator_instruction_template.format(targetType=target_type)
    # state[target_type] = [state[target_type]]
    state['variables'] = []
    state["objective"] = [state["objective"]]

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
            prompt = formulator_prompt_template.format(
                background=state["background"],
                targetType=target_type,
                # targetDescription=target["description"],
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

    print('state')
    print(json.dumps(state, indent=4))
    print("="*20)

    # formulation_start = output.find('"formulation"')
    # auxiliary_constraints_start = output.find('"auxiliary_constraints"')
    # while output[auxiliary_constraints_start] != "}":
    #     auxiliary_constraints_start -= 1
    # while output[auxiliary_constraints_start] != '"':
    #     auxiliary_constraints_start -= 1
