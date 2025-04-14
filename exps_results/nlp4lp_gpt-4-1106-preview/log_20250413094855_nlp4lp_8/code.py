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
QuantityProduced = model.addVars(NumParts, vtype=gp.GRB.INTEGER, name="QuantityProduced")

# Add constraint for non-negative quantity produced
for k in range(NumParts):
    model.addConstr(QuantityProduced[k] >= 0, name="nonnegativity_constraint_{}".format(k))

# Total time used on each machine for all spare parts cannot exceed the machine's monthly capacity
for s in range(NumMachines):
    model.addConstr(gp.quicksum(Time[k, s] * QuantityProduced[k] for k in range(NumParts)) <= Capacity[s], name=f"machine_capacity_{s}")

# Add production time capacity constraints for each machine
for s in range(NumMachines):
    model.addConstr(gp.quicksum(Time[k, s] * QuantityProduced[k] for k in range(NumParts)) <= Capacity[s], name=f"machine_capacity_{s}")

# Set objective
model.setObjective(gp.quicksum(Profit[k] * QuantityProduced[k] for k in range(NumParts)), gp.GRB.MAXIMIZE)

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
