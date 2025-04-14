import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/35/data.json", "r") as f:
    data = json.load(f)

NumProducts = data["NumProducts"] # scalar parameter
NumMachines = data["NumMachines"] # scalar parameter
ProduceTime = np.array(data["ProduceTime"]) # ['NumProducts', 'NumMachines']
AvailableTime = np.array(data["AvailableTime"]) # ['NumMachines']
Profit = np.array(data["Profit"]) # ['NumProducts']
ProductionQuantity = model.addVars(NumProducts, vtype=gp.GRB.CONTINUOUS, name="ProductionQuantity")

# Add non-negativity constraints for product quantities
for k in range(NumProducts):
    model.addConstr(ProductionQuantity[k] >= 0, name=f"non_negativity_product_{k}")

# Add production time constraints for each machine
for m in range(NumMachines):
    model.addConstr(
        gp.quicksum(ProductionQuantity[k] * ProduceTime[k, m] for k in range(NumProducts)) <= AvailableTime[m],
        name=f"production_time_machine_{m}"
    )

# Add constraints to ensure the total production time on each machine does not exceed its available time
for m in range(NumMachines):
    model.addConstr(
        gp.quicksum(ProduceTime[k, m] * ProductionQuantity[k] for k in range(NumProducts)) <= AvailableTime[m],
        name=f"machine_time_constraint_{m}"
    )

# Set objective
model.setObjective(gp.quicksum(Profit[k] * ProductionQuantity[k] for k in range(NumProducts)), gp.GRB.MAXIMIZE)

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
