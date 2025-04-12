import json
import traceback
from openai import OpenAI, Client
from template_loader import TemplateLoader

class Evaluator:
    def __init__(self, client:Client, model:str):
        self.client = client
        self.model = model
        self.seed = 2
        self.solver = 'gurobipy'

    def run(self, state:dict, templates:TemplateLoader):
        local_env = {}
        code = ""
        last_line = ""
        bogus_context = None

        try:
            last_line = templates['prep_code'].format(solver_prep_code=templates['solver_prep_code'], data_json_path=state['problem_path']+"data.json")
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
            state["prep_code"] = templates['prep_code'].format(solver_prep_code=templates['solver_prep_code'], data_json_path=state['problem_path']+"data.json")
            code += last_line + "\n"

            # if not res["bogus_context"]:
            #     return f"Bad model! Print DONE to finish the execution.", state

            res["bogus_context"]["status"] = "runtime_error"
            state["solver_output_status"] = res["bogus_context"]["status"]

        else:
            state["solution_status"] = "solved"
            state["solver_output_status"] = res["status"]
            state["obj_val"] = res["obj_val"]
            state["code"] = res["code"]