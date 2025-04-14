import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_200/data.json", "r") as f:
    data = json.load(f)

HamSlicerHours = data["HamSlicerHours"] # scalar parameter
HamPackerHours = data["HamPackerHours"] # scalar parameter
RibSlicerHours = data["RibSlicerHours"] # scalar parameter
RibPackerHours = data["RibPackerHours"] # scalar parameter
MaxHours = data["MaxHours"] # scalar parameter
HamProfit = data["HamProfit"] # scalar parameter
RibProfit = data["RibProfit"] # scalar parameter
HamBatches = model.addVar(vtype=gp.GRB.CONTINUOUS, name="HamBatches")
RibBatches = model.addVar(vtype=gp.GRB.CONTINUOUS, name="RibBatches")

# Ensure the number of batches of hams produced is non-negative
model.addConstr(HamBatches >= 0, name="non_negative_ham_batches")

# No code is needed because non-negativity is inherent to the variable type (CONTINUOUS), which is already defined.

# Add constraint for total slicer hours for hams and pork ribs
model.addConstr(
    HamBatches * HamSlicerHours + RibBatches * RibSlicerHours <= MaxHours, 
    name="slicer_hours_constraint"
)

# Add constraint for total packer hours
model.addConstr(
    HamPackerHours * HamBatches + RibPackerHours * RibBatches <= MaxHours,
    name="packer_hours_constraint"
)

# Add slicer time constraint
model.addConstr(HamSlicerHours * HamBatches + RibSlicerHours * RibBatches <= MaxHours, 
                name="slicer_time_constraint")

# Add packer time constraints
model.addConstr(
    HamPackerHours * HamBatches + RibPackerHours * RibBatches <= MaxHours,
    name="packer_time_constraint"
)

# Set objective
model.setObjective(HamProfit * HamBatches + RibProfit * RibBatches, gp.GRB.MAXIMIZE)

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
