import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/66/data.json", "r") as f:
    data = json.load(f)

N = data["N"] # scalar parameter
StartCity = data["StartCity"] # scalar parameter
Distances = np.array(data["Distances"]) # ['N', 'N']
Visit = model.addVars(N, N, vtype=gp.GRB.BINARY, name="Visit")

Visit = model.addVars(N, N, vtype=gp.GRB.BINARY, name='Visit')

# Constraint for returning to StartCity after visiting all other towns
model.addConstr(gp.quicksum(Visit[StartCity, j] for j in range(N) if j != StartCity) == 1, name="return_from_others_to_StartCity")
model.addConstr(gp.quicksum(Visit[i, StartCity] for i in range(N) if i != StartCity) == 1, name="return_to_StartCity_from_others")

# The distance between any two towns is non-negative - this is an inherent property.
# Hence, no code needed to enforce this as a constraint in the optimization model.
# Distances are parameters and not variables and should be ensured non-negative when inputted.

# Each town must have exactly one departure, except for the start city
for j in range(N):
    if j != StartCity:
        model.addConstr(gp.quicksum(Visit[i, j] for i in range(N) if i != j) == 1,
                        name=f"one_departure_town_{j}")

# No code needed since the constraint is already defined by the variables' binary nature and only requires the variables to be distinct.
# The given variable definition `Visit` is binary and accounts for i != j implicitly in its structure.

# Objective: Minimize the total travel distance
model.setObjective(gp.quicksum(Distances[i, j] * Visit[i, j] for i in range(N) for j in range(N) if i != j), gp.GRB.MINIMIZE)

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
