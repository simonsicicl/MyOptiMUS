import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/1/data.json", "r") as f:
    data = json.load(f)

M = data["M"] # scalar parameter
N = data["N"] # scalar parameter
Available = np.array(data["Available"]) # ['N']
Requirements = np.array(data["Requirements"]) # ['M', 'N']
Prices = np.array(data["Prices"]) # ['M']
ProducedQuantities = model.addVars(M, vtype=gp.GRB.CONTINUOUS, name="ProducedQuantities")

# Add non-negativity constraints for production quantities
for i in range(M):
    model.addConstr(ProducedQuantities[i] >= 0, name=f"non_negativity_{i}")

# Add raw material usage constraints
for j in range(N):
    model.addConstr(
        gp.quicksum(ProducedQuantities[i] * Requirements[i, j] for i in range(M)) <= Available[j],
        name=f"raw_material_usage_{j}"
    )

# Set objective
model.setObjective(gp.quicksum(ProducedQuantities[i] * Prices[i] for i in range(M)), gp.GRB.MAXIMIZE)

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
