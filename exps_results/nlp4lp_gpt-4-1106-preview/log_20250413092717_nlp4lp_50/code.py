import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/50/data.json", "r") as f:
    data = json.load(f)

NumShifts = data["NumShifts"] # scalar parameter
OfficersNeeded = np.array(data["OfficersNeeded"]) # ['NumShifts']
ShiftCosts = np.array(data["ShiftCosts"]) # ['NumShifts']
OfficersPerShift = model.addVars(NumShifts, vtype=gp.GRB.INTEGER, name="OfficersPerShift")

# Ensure the number of officers assigned to each shift is non-negative
for s in range(NumShifts):
    model.addConstr(OfficersPerShift[s] >= 0, name=f"non_negativity_shift_{s}")

# Ensure each shift has at least the required number of officers assigned
for s in range(NumShifts):
    model.addConstr(OfficersPerShift[s] >= OfficersNeeded[s], name=f"min_officers_shift{s}")

# Set objective
model.setObjective(gp.quicksum(OfficersPerShift[s] * ShiftCosts[s] for s in range(NumShifts)), gp.GRB.MINIMIZE)

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
