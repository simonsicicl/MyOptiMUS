import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/4/data.json", "r") as f:
    data = json.load(f)

T = data["T"] # scalar parameter
Period = data["Period"] # scalar parameter
Demand = np.array(data["Demand"]) # ['T']
NumberOfNurses = model.addVars(T, vtype=gp.GRB.CONTINUOUS, name="NumberOfNurses")
HiredNurses = model.addVar(vtype=gp.GRB.INTEGER, name="HiredNurses")

# Add non-negativity constraints for the number of nurses assigned each day
for t in range(T):
    model.addConstr(NumberOfNurses[t] >= 0, name=f"non_negativity_nurses_day_{t}")

# Add constraints to ensure the number of nurses assigned each day meets or exceeds the demand
for t in range(T):
    model.addConstr(NumberOfNurses[t] >= Demand[t], name=f"demand_meet_day_{t}")

# Add constraint to ensure the number of nurses assigned on any day does not exceed the total number of nurses hired
for t in range(T):
    model.addConstr(NumberOfNurses[t] <= HiredNurses, name=f"nurses_limit_day_{t}")

# Add constraints to ensure enough nurses are assigned each day to meet the daily demand
for t in range(T):
    model.addConstr(NumberOfNurses[t] >= Demand[t], name=f"demand_satisfaction_day_{t}")

# Set objective
model.setObjective(HiredNurses, gp.GRB.MINIMIZE)

# Optimize model
model.optimize()


# Get model status
status = model.status

obj_val = None
# check whether the model is infeasible, has infinite solutions, or has an optimal solution
if status == gp.GRB.INFEASIBLE:
    obj_val = "infeasible"
elif status == gp.GRB.INF_OR_UNBD:
    obj_val = "infeasible or unbounded"
elif status == gp.GRB.UNBOUNDED:
    obj_val = "unbounded"
elif status == gp.GRB.OPTIMAL:
    obj_val = model.objVal
