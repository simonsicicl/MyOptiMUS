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

        while self.conversation_state["round"] < self.max_rounds:
            print("=" * 40)
            print("=" * 40)
            print("Round", self.conversation_state["round"])

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

            completion = self.client.chat.completions.create(model=self.model, messages=messages, seed=self.seed)
            response = completion.choices[0].message.content
            

            decision = response.strip()
            if "```json" in decision:
                decision = decision.split("```json")[1].split("```")[0]
            decision = decision.replace("\\", "")
            print(decision)

            if decision == "DONE":
                print("DONE")
                return "The problem is solved.", state
            
            decision = json.loads(decision)
        
            print("---- History:\n", "\n".join([json.dumps(item[0]) for item in self.history]))

            print(f"\n---- Decision:||{decision}||\n")

            if not decision["agent_name"] in [agent.name for agent in self.agents]:
                raise ValueError(f"Decision {decision} is not a valid agent name. Please choose from {self.agents}")
            
            agent = [each for each in self.agents if each.name == decision["agent_name"]][0]

            message, state = agent.run(state=state)

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
        return "The problem is not solved.", state