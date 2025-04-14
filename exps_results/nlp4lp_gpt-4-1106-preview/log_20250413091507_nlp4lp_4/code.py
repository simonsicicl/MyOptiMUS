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
NumberOfNurses = model.addVars(T, vtype=gp.GRB.INTEGER, name="NumberOfNurses")

# Ensure a non-negative number of nurses for each day
for t in range(T):
    model.addConstr(NumberOfNurses[t] >= 0, name=f"non_negative_nurses_day_{t}")

NumberOfNurses = model.addVars(T, vtype=gp.GRB.INTEGER, name="NumberOfNurses")

# Constraint: Number of nurses on each day must meet the daily demand
for t in range(T):
    model.addConstr(NumberOfNurses[t] >= Demand[t], name=f"demand_day_{t}")

# Set objective
model.setObjective(gp.quicksum(NumberOfNurses[t] for t in range(T)), gp.GRB.MINIMIZE)

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
