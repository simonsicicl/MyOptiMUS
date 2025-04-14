import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/60/data.json", "r") as f:
    data = json.load(f)

N = data["N"] # scalar parameter
W = data["W"] # scalar parameter
WestTime = np.array(data["WestTime"]) # ['N', 'W-1']
NorthTime = np.array(data["NorthTime"]) # ['N-1', 'W']
EastWestUsage = model.addVars(N, range(W-1), vtype=gp.GRB.BINARY, name="EastWestUsage")
NorthSouthUsage = model.addVars(N-1, W, vtype=gp.GRB.BINARY, name="NorthSouthUsage")

# Constrain the total number of east-west street segments used to not exceed N
east_west_usage_constraint = gp.quicksum(EastWestUsage[n, w] for n in range(N) for w in range(W-1))
model.addConstr(east_west_usage_constraint <= N, name="east_west_usage_limit")

# Constraint: Total number of north-south street segments used cannot exceed W
model.addConstr(gp.quicksum(NorthSouthUsage[n, w] for n in range(N-1) for w in range(W)) <= W, name="north_south_usage_limit")

# Ensure east-west street segments used are non-negative (no need for an explicit constraint for a binary variable)
# Since EastWestUsage is defined as a binary variable, it is inherently non-negative.
# Hence, no additional code is necessary for this constraint.

# Since NorthSouthUsage is already a binary variable, no further constraints are needed to ensure its values are between 0 and 1.
# The binary nature of the variable inherently imposes this constraint.
# Therefore, no code is required.

# Define the objective function
objective = gp.quicksum(EastWestUsage[n,w] * WestTime[n,w] for n in range(N) for w in range(W-1)) \
          + gp.quicksum(NorthSouthUsage[n,w] * NorthTime[n,w] for n in range(N-1) for w in range(W))

# Set the objective
model.setObjective(objective, gp.GRB.MINIMIZE)

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
