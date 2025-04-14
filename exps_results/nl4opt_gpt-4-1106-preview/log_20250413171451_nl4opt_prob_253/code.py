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
NumberOfSmallBoxes = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfSmallBoxes")
NumberOfLargeBoxes = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfLargeBoxes")

# Since NumberOfSmallBoxes is already defined as an integer variable, we just need to add a non-negativity constraint
model.addConstr(NumberOfSmallBoxes >= 0, name="non_negativity_small_boxes")

# Constraint to ensure the number of large boxes used for shipping is non-negative
model.addConstr(NumberOfLargeBoxes >= 0, name="nonnegativity_large_boxes")

# Add constraint for the minimum ratio of the number of small boxes to large boxes
model.addConstr(NumberOfSmallBoxes >= MinSmallToLargeRatio * NumberOfLargeBoxes, name="min_small_to_large_ratio_constraint")

# Constraint for minimum number of large boxes
model.addConstr(NumberOfLargeBoxes >= MinLargeBoxes, name="min_large_boxes")

# Ensure at least MinMasksRequired masks are distributed
model.addConstr(NumberOfSmallBoxes * SmallBoxCapacity + NumberOfLargeBoxes * LargeBoxCapacity >= MinMasksRequired, name="min_masks_required")

# Ensure that the number of masks shipped meets or exceeds the minimum required
model.addConstr(NumberOfSmallBoxes * SmallBoxCapacity + NumberOfLargeBoxes * LargeBoxCapacity >= MinMasksRequired, name="MinMasksRequirement")

# Maintain the minimum required ratio of small boxes to large boxes
model.addConstr(NumberOfSmallBoxes >= MinSmallToLargeRatio * NumberOfLargeBoxes, name="min_small_to_large_ratio")

# Ensure that the number of large boxes used is at least the minimum required
model.addConstr(NumberOfLargeBoxes >= MinLargeBoxes, name="min_large_boxes_constraint")

# Set objective
model.setObjective(NumberOfSmallBoxes + NumberOfLargeBoxes, gp.GRB.MINIMIZE)

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
