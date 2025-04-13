import json
from openai import OpenAI, Client
from template_loader import TemplateLoader
from agent import Agent

class Manager(Agent):
    def __init__(self, client:Client, model:str, templates:TemplateLoader, agents: list[Agent], max_rounds: int = 12):
        super().__init__(
            name="Manager",
            description="This is a manager agent that chooses which agent to work on the problem next and organizes the conversation within its team.",
            client=client, model=model, templates=templates
            )
        self.agents = agents
        self.max_rounds = max_rounds
        self.conversation_state = {"round": 0}
        self.history = []

    def run(self, state:dict) -> tuple[str, dict]: 
        self.history = []

        for parameter in state["parameters"]:
            # assert "shape" in parameter.keys(), "Parameter: Shape is not defined"
            # assert "symbol" in parameter.keys(), "Parameter: Symbol is not defined"
            # assert ("definition" in parameter.keys() and len(parameter["definition"]) > 0), "Parameter: definition is not defined"
            if not "shape" in parameter.keys():
                return ("CRASHED", state)
            if not "symbol" in parameter.keys():
                return ("CRASHED", state)
            if not ("definition" in parameter.keys() and len(parameter["definition"]) > 0):
                return ("CRASHED", state)

            if parameter["shape"]:
                code_symbol = parameter["symbol"].split("_")[0]
                parameter["code"] = (f'{code_symbol} = np.array(data["{code_symbol}"]) # {parameter["shape"]}')
            else:
                code_symbol = parameter["symbol"].split("_")[0]
                parameter["code"] = (f'{code_symbol} = data["{code_symbol}"] # scalar parameter')
        try:
            for target in ["constraints", "objective"]:
                state[target] = [{"description": x, "status": "not_formulated"} for x in state[target]]
        except:
            return ("CRASHED", state)

        while self.conversation_state["round"] <= self.max_rounds:
            try:
                print("Round", self.conversation_state["round"], end=':')

                agents_list = "".join(["-" + agent.name + ": " + agent.description + "\n" for agent in self.agents])

                messages = [
                    {"role": "developer", "content": self.templates['manager_instruction']},
                    {
                        "role": "user", 
                        "content": self.templates['manager_prompt'].format(
                            agents=agents_list,
                            history="\n".join([json.dumps(item[0]) for item in self.history])
                        )
                    }
                ]
            except:
                return ("CRASHED", state)

            for cnt in range(2, -2, -1):
                # assert cnt >= 0, "\n    Invalid decision!"
                if cnt < 0:
                    return ("CRASHED", state)
                try:
                    completion = self.client.chat.completions.create(model=self.model, messages=messages, seed=cnt)
                    response = completion.choices[0].message.content
                    decision = response.strip()
                    if "```json" in decision:
                        decision = decision.split("```json")[1].split("```")[0]
                    decision = decision.replace("\\", "")
                    if decision == "DONE":
                        state['round'] = self.conversation_state["round"]
                        state['agent_calls'] = {
                            'Formulator': 0,
                            'Programmer': 0,
                            'Evaluator': 0
                        }
                        for each in self.history:
                            state['agent_calls'][each[0]['agent_name']] += 1
                        print(" The problem is SOLVED!")
                        return "The problem is solved.", state
                    decision = json.loads(decision)
                    break
                except Exception as e:
                    print("\n    Invalid decision! Trying again ...")
                
        
            # print("---- History:\n", "\n".join([json.dumps(item[0]) for item in self.history]))

            # print(f"\n---- Decision:||{decision}||\n")
            try:
                print(f" {decision["agent_name"]}\t\t{decision["task"]}")

                if not decision["agent_name"] in [agent.name for agent in self.agents]:
                    raise ValueError(f"Decision {decision} is not a valid agent name. Please choose from {self.agents}")
                
                agent = [each for each in self.agents if each.name == decision["agent_name"]][0]

                message, state = agent.run(state=state)

                if message == "CRASHED":
                    return ("CRASHED", state)

                # print(message)

                with open(f"{state['log_path']}log_{self.conversation_state['round']}.json", "w") as f:
                    json.dump(state, f, indent=4)

                decision["result"] = message
                self.history.append((decision, state))

                with open(state["log_path"] + "selection_log.json", "w") as f:
                    json.dump([d for (d, s) in self.history], f, indent=4)

                if "code" in state:
                    with open(state["log_path"] + "code.py", "w") as f:
                        f.write(state["code"])

                self.conversation_state["round"] += 1
            except:
                return ("CRASHED", state)
        print("The problem is NOT SOLVED!")
        return "The problem is NOT SOLVED!", state