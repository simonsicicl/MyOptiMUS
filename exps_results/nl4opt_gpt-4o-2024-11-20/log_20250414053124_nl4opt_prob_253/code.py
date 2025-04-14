import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_253/data.json", "r") as f:
    data = json.load(f)

SmallBoxCapacity = data["SmallBoxCapacity"] # scalar parameter
LargeBoxCapacity = data["LargeBoxCapacity"] # scalar parameter
MinSmallToLargeRatio = data["MinSmallToLargeRatio"] # scalar parameter
MinLargeBoxes = data["MinLargeBoxes"] # scalar parameter
MinMasksRequired = data["MinMasksRequired"] # scalar parameter
SmallBoxes = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SmallBoxes")
LargeBoxes = model.addVar(vtype=gp.GRB.CONTINUOUS, name="LargeBoxes")

# The non-negativity constraint for SmallBoxes is implicitly satisfied by its continuous type which is non-negative by default in Gurobi. Hence, no additional code is required.

# No additional code needed because the variable "LargeBoxes" is already defined as non-negative due to its default properties in gurobipy (lower bound of 0).

# Add constraint for the minimum ratio of small boxes to large boxes
model.addConstr(SmallBoxes >= MinSmallToLargeRatio * LargeBoxes, name="min_small_to_large_ratio")

# Add constraint that the number of large boxes used must be at least MinLargeBoxes
model.addConstr(LargeBoxes >= MinLargeBoxes, name="min_large_boxes_constraint")

# Add constraint to ensure the total number of masks distributed meets or exceeds the minimum required
model.addConstr(
    SmallBoxes * SmallBoxCapacity + LargeBoxes * LargeBoxCapacity >= MinMasksRequired,
    name="min_masks_required"
)

# Ensure the total number of masks shipped meets or exceeds the minimum required
model.addConstr(
    SmallBoxes * SmallBoxCapacity + LargeBoxes * LargeBoxCapacity >= MinMasksRequired,
    name="min_masks_requirement"
)

# Add constraint to ensure SmallBoxes meet the minimum ratio with respect to LargeBoxes
model.addConstr(SmallBoxes >= MinSmallToLargeRatio * LargeBoxes, name="min_small_to_large_ratio")

# Add constraint to ensure the number of large boxes meets the minimum required number
model.addConstr(LargeBoxes >= MinLargeBoxes, name="min_large_boxes")

# Set objective
model.setObjective(SmallBoxes + LargeBoxes, gp.GRB.MINIMIZE)

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
