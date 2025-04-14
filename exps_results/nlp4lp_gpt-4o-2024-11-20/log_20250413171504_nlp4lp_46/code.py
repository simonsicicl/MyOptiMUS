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
ProductsProduced = model.addVars(M, vtype=gp.GRB.CONTINUOUS, name="ProductsProduced")

# Add raw material usage constraints
for i in range(N):
    model.addConstr(
        gp.quicksum(Requirements[i, j] * ProductsProduced[j] for j in range(M)) <= Available[i],
        name=f"raw_material_usage_{i}"
    )

# Add raw material consumption constraints
for i in range(N):
    model.addConstr(
        gp.quicksum(Requirements[i, j] * ProductsProduced[j] for j in range(M)) <= Available[i],
        name=f"raw_material_constraint_{i}"
    )

# Add production-demand constraints
for j in range(M):
    model.addConstr(ProductsProduced[j] <= Demands[j], name=f"production_demand_{j}")

# Add non-negativity constraints for produced products
for j in range(M):
    model.addConstr(ProductsProduced[j] >= 0, name=f"non_negativity_product_{j}")

# Add raw material consumption constraints
for i in range(N):
    model.addConstr(
        gp.quicksum(Requirements[i, j] * ProductsProduced[j] for j in range(M)) <= Available[i],
        name=f"raw_material_constraint_{i}"
    )

# Add production-demand constraints
for j in range(M):
    model.addConstr(ProductsProduced[j] <= Demands[j], name=f"demand_constraint_{j}")

# Add non-negativity constraints for production quantities
for j in range(M):
    model.addConstr(ProductsProduced[j] >= 0, name=f"non_negative_production_{j}")

# Set objective
model.setObjective(gp.quicksum(ProductsProduced[j] * (Prices[j] - Costs[j]) for j in range(M)), gp.GRB.MAXIMIZE)

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
