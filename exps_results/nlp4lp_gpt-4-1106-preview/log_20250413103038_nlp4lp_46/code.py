import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/46/data.json", "r") as f:
    data = json.load(f)

N = data["N"] # scalar parameter
M = data["M"] # scalar parameter
Available = np.array(data["Available"]) # ['N']
Requirements = np.array(data["Requirements"]) # ['N', 'M']
Prices = np.array(data["Prices"]) # ['M']
Costs = np.array(data["Costs"]) # ['M']
Demands = np.array(data["Demands"]) # ['M']
X = model.addVars(M, vtype=gp.GRB.CONTINUOUS, name="X")

# Raw materials usage constraint
for i in range(N):
    model.addConstr(gp.quicksum(Requirements[i, j] * X[j] for j in range(M)) <= Available[i], name=f"raw_material_usage_{i}")

# Each product's production must not exceed the raw material requirements per unit
for i in range(N):
    model.addConstr(gp.quicksum(Requirements[i, j] * X[j] for j in range(M)) <= Available[i], name=f"raw_material_requirements_{i}")

# Each product's production should not exceed its market demand
for j in range(M):
    model.addConstr(X[j] <= Demands[j], name=f"demand_limit_{j}")

# Add non-negativity constraints for the number of units produced for each product
for j in range(M):
    model.addConstr(X[j] >= 0, name=f"nonnegativity_{j}")

# Constraint: Production should not exceed available amount of raw materials
for i in range(N):
    model.addConstr(gp.quicksum(Requirements[i, j] * X[j] for j in range(M)) <= Available[i], name=f"raw_material_limit_{i}")

# Ensure that the production does not exceed the market demands for each product
for j in range(M):
    model.addConstr(X[j] <= Demands[j], name=f"market_demand_{j}")

# Set objective
model.setObjective(gp.quicksum((Prices[j] - Costs[j]) * X[j] for j in range(M)), gp.GRB.MAXIMIZE)

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
