import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/56/data.json", "r") as f:
    data = json.load(f)

NumTerminals = data["NumTerminals"] # scalar parameter
NumDestinations = data["NumDestinations"] # scalar parameter
Cost = np.array(data["Cost"]) # ['NumTerminals', 'NumDestinations']
Demand = np.array(data["Demand"]) # ['NumDestinations']
Supply = np.array(data["Supply"]) # ['NumTerminals']
TransportedQuantity = model.addVars(NumTerminals, NumDestinations, vtype=gp.GRB.CONTINUOUS, name="TransportedQuantity")

# Add constraints for non-negative transported quantities from terminals to destinations
for i in range(NumTerminals):
    for j in range(NumDestinations):
        model.addConstr(TransportedQuantity[i, j] >= 0, name=f"non_negative_transported_qty_{i}_{j}")

# Add constraints to ensure transported quantity from each terminal does not exceed its supply
for i in range(NumTerminals):
    model.addConstr(gp.quicksum(TransportedQuantity[i, j] for j in range(NumDestinations)) <= Supply[i], name=f"supply_constraint_terminal_{i}")

# Ensure demand at each destination is met by the sum of transported quantities from all terminals
for j in range(NumDestinations):
    model.addConstr(gp.quicksum(TransportedQuantity[i, j] for i in range(NumTerminals)) >= Demand[j], name=f"Demand_met_{j}")

# Set objective
model.setObjective(gp.quicksum(Cost[i, j] * TransportedQuantity[i, j] for i in range(NumTerminals) for j in range(NumDestinations)), gp.GRB.MINIMIZE)

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
