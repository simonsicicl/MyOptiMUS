import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_156/data.json", "r") as f:
    data = json.load(f)

VanCapacity = data["VanCapacity"] # scalar parameter
TruckCapacity = data["TruckCapacity"] # scalar parameter
MinPairs = data["MinPairs"] # scalar parameter
VansUsed = model.addVar(vtype=gp.GRB.INTEGER, name="VansUsed")
TrucksUsed = model.addVar(vtype=gp.GRB.INTEGER, name="TrucksUsed")

# Add constraint for minimum pairs of shoes to be supplied
model.addConstr(VanCapacity * VansUsed + TruckCapacity * TrucksUsed >= MinPairs, name="min_pairs_supplied")

model.addConstr(TrucksUsed <= VansUsed, name="trucks_leq_vans")

# The number of vans must be non-negative. Since VansUsed is already an integer variable, no further action is needed.
model.addConstr(VansUsed >= 0, "non_negativity_vans")

# Ensure the sum of shoe supplies delivered meets minimum delivery requirement
model.addConstr(VanCapacity * VansUsed + TruckCapacity * TrucksUsed >= MinPairs, name="delivery_requirement")

model.addConstr(TrucksUsed <= VansUsed, "trucks_leq_vans")

# Set objective
model.setObjective(VansUsed, gp.GRB.MINIMIZE)

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
