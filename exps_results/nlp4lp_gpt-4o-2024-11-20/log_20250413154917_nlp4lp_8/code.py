import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/8/data.json", "r") as f:
    data = json.load(f)

NumParts = data["NumParts"] # scalar parameter
NumMachines = data["NumMachines"] # scalar parameter
Time = np.array(data["Time"]) # ['NumParts', 'NumMachines']
Profit = np.array(data["Profit"]) # ['NumParts']
Capacity = np.array(data["Capacity"]) # ['NumMachines']
ProducedQuantity = model.addVars(NumParts, vtype=gp.GRB.CONTINUOUS, name="ProducedQuantity")

# Add non-negativity constraints for spare part quantities produced
for k in range(NumParts):
    model.addConstr(ProducedQuantity[k] >= 0, name=f"non_negativity_{k}")

# Add machine capacity constraints
for s in range(NumMachines):
    model.addConstr(
        gp.quicksum(ProducedQuantity[k] * Time[k, s] for k in range(NumParts)) <= Capacity[s],
        name=f"machine_capacity_{s}"
    )

# Add machine capacity constraints
for s in range(NumMachines):
    model.addConstr(
        gp.quicksum(Time[k, s] * ProducedQuantity[k] for k in range(NumParts)) <= Capacity[s], 
        name=f"machine_capacity_{s}"
    )

# Add non-negativity constraints for production quantities
for k in range(NumParts):
    model.addConstr(ProducedQuantity[k] >= 0, name=f"non_negativity_{k}")

# Set objective
model.setObjective(gp.quicksum(Profit[k] * ProducedQuantity[k] for k in range(NumParts)), gp.GRB.MAXIMIZE)

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
