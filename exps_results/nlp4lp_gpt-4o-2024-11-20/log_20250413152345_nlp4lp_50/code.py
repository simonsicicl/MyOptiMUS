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
OfficersAssigned = model.addVars(NumShifts, vtype=gp.GRB.CONTINUOUS, name="OfficersAssigned")

# Add non-negativity constraints for the number of officers assigned to each shift
for s in range(NumShifts):
    model.addConstr(OfficersAssigned[s] >= 0, name=f"non_negativity_officers_shift_{s}")

# Add constraints to ensure the number of officers assigned equals the officers needed for each shift
for s in range(NumShifts):
    model.addConstr(OfficersAssigned[s] == OfficersNeeded[s], name=f"officers_assignment_{s}")

# Add constraints to ensure the required number of officers are assigned to each shift
for s in range(NumShifts):
    model.addConstr(OfficersAssigned[s] >= OfficersNeeded[s], name=f"MinOfficersShift{s}")

# Set objective
model.setObjective(gp.quicksum(ShiftCosts[s] * OfficersAssigned[s] for s in range(NumShifts)), gp.GRB.MINIMIZE)

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
