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
EastWestUsed = model.addVars(N, W-1, vtype=gp.GRB.BINARY, name="EastWestUsed")
RouteDecision = model.addVars(N, W-1, vtype=gp.GRB.BINARY, name="RouteDecision")
NorthSouthUsed = model.addVars(N-1, W, vtype=gp.GRB.BINARY, name="NorthSouthUsed")

# Add constraint to limit the total number of east-west street segments used
model.addConstr(
    gp.quicksum(EastWestUsed[n, w] for n in range(N) for w in range(W - 1)) <= N,
    name="limit_east_west_segments"
)

# Add constraint to ensure the number of north-south street segments used does not exceed W
model.addConstr(
    gp.quicksum(NorthSouthUsed[n, w] for n in range(N-1) for w in range(W)) <= W,
    name="limit_north_south_segments"
)

# EastWestUsed is binary (non-negative by definition), so this constraint is not required.

# No additional code needed as gurobipy automatically enforces non-negativity constraints for binary variables.

# Add constraints to ensure EastWestUsed is marked if a RouteDecision is made
for n in range(N):
    for w in range(W-1):
        model.addConstr(EastWestUsed[n, w] >= RouteDecision[n, w], name=f"east_west_segment_use_{n}_{w}")

# Add constraints to ensure an east-west segment cannot be marked as used if it is not part of the route.
for n in range(N):
    for w in range(W-1):
        model.addConstr(EastWestUsed[n, w] <= RouteDecision[n, w], name=f"EastWestSegmentNotUsed_{n}_{w}")

# Add activation constraints linking NorthSouthUsed and RouteDecision variables
for n in range(N-1):
    for w in range(W-1):
        model.addConstr(NorthSouthUsed[n, w] >= RouteDecision[n, w] + RouteDecision[n+1, w] - 1, name=f"activation_constraint_{n}_{w}")

# Add flow conservation constraints
for n in range(N):
    for w in range(W):
        model.addConstr(
            gp.quicksum(EastWestUsed[n, ww] for ww in range(W-1)) +
            gp.quicksum(NorthSouthUsed[nn, w] for nn in range(N-1)) <= 1,
            name=f"flow_conservation_{n}_{w}"
        )

# Add constraints to ensure that segments used in the route align with the overall route decision plan
for n in range(N):
    for w in range(W - 1):
        model.addConstr(RouteDecision[n, w] >= EastWestUsed[n, w] + (NorthSouthUsed[n - 1, w] if n > 0 else 0) + (NorthSouthUsed[n, w] if n < N - 1 else 0), name=f"route_decision_alignment_{n}_{w}")

# Set objective
model.setObjective(
    gp.quicksum(WestTime[n, w] * EastWestUsed[n, w] for n in range(N) for w in range(W-1)) +
    gp.quicksum(NorthTime[n, w] * NorthSouthUsed[n, w] for n in range(N-1) for w in range(W)),
    gp.GRB.MINIMIZE
)

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
