import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_153/data.json", "r") as f:
    data = json.load(f)

OldVanCapacity = data["OldVanCapacity"] # scalar parameter
NewVanCapacity = data["NewVanCapacity"] # scalar parameter
OldVanPollution = data["OldVanPollution"] # scalar parameter
NewVanPollution = data["NewVanPollution"] # scalar parameter
MinBottles = data["MinBottles"] # scalar parameter
MaxNewVans = data["MaxNewVans"] # scalar parameter
NumberOfOldVans = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfOldVans")
NumberOfNewVans = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfNewVans")

model.addConstr(NumberOfOldVans >= 0, "non_negativity_old_vans")

# Since NumberOfNewVans is already defined as an integer variable, no additional constraint is needed.
# Non-negativity is implicit in the variable definition when using model.addVar() with vtype=GRB.INTEGER.

# Ensure at least MinBottles are delivered using the old and new vans
model.addConstr(NumberOfOldVans * OldVanCapacity + NumberOfNewVans * NewVanCapacity >= MinBottles, "min_bottles_delivery")

model.addConstr(NumberOfNewVans <= MaxNewVans, name="max_new_vans_constraint")

# Add constraint to ensure total number of bottles delivered meets/exceeds the required minimum amount
model.addConstr(NumberOfOldVans * OldVanCapacity + NumberOfNewVans * NewVanCapacity >= MinBottles, "min_bottles_delivery")

# Constraint for maximum number of new vans
model.addConstr(NumberOfNewVans <= MaxNewVans, name="max_new_vans")

# Set objective
model.setObjective(NumberOfOldVans * OldVanPollution + NumberOfNewVans * NewVanPollution, gp.GRB.MINIMIZE)

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
