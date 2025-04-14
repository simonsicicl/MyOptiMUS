import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/14/data.json", "r") as f:
    data = json.load(f)

M = data["M"] # scalar parameter
N = data["N"] # scalar parameter
A = np.array(data["A"]) # ['M', 'N']
B = np.array(data["B"]) # ['M']
Radius = model.addVar(vtype=gp.GRB.CONTINUOUS, name="Radius")
Center = model.addVars(N, vtype=gp.GRB.CONTINUOUS, name="Center")

# Radius of balls must be non-negative
model.addConstr(Radius >= 0, name="non_negative_radius")

# Ensure the ball is completely within the set P
for i in range(M):
    model.addQConstr(
        gp.quicksum(A[i][j] * Center[j] for j in range(N)) -
        gp.quicksum((Radius * A[i][j]) * (Radius * A[i][j]) for j in range(N)) <= B[i],
        name=f"ball_within_set_P_{i}"
    )

# Add constraint to ensure the ball is entirely within the polytope P
for i in range(M):
    lhs = gp.quicksum(A[i,j] * Center[j] for j in range(N))
    model.addConstr(lhs <= B[i], name=f"polytope_containment_{i}")
    model.addQConstr(gp.quicksum(A[i, j]**2 for j in range(N)) * Radius**2 <= B[i]**2, name=f"sphere_containment_{i}")

# Set objective
model.setObjective(Radius, gp.GRB.MAXIMIZE)

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
