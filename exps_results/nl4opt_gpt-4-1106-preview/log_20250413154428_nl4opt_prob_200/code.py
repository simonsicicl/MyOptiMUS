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
PorkRibBatches = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PorkRibBatches")

# Add constraint to ensure the number of ham batches is non-negative
model.addConstr(HamBatches >= 0, name="non_negative_ham_batches")

# Add constraint to ensure the number of pork rib batches is non-negative
model.addConstr(PorkRibBatches >= 0, name="non_negative_pork_rib_batches")

# Add slicer hours constraint
model.addConstr(HamBatches * HamSlicerHours + PorkRibBatches * RibSlicerHours <= MaxHours, name="slicer_hours_constraint")

# Add constraint for total packer hours for hams and pork ribs not to exceed max operating hours
model.addConstr(HamBatches * HamPackerHours + PorkRibBatches * RibPackerHours <= MaxHours, name="packer_hours_limit")

# Add constraint for total operating hours of the meat slicer
model.addConstr(HamSlicerHours * HamBatches + RibSlicerHours * PorkRibBatches <= MaxHours, "meat_slicer_operating_hours")

# Add constraint for maximum operating hours of the meat packer
model.addConstr(HamPackerHours * HamBatches + RibPackerHours * PorkRibBatches <= MaxHours, name="max_operating_hours")

# Set objective function
model.setObjective(HamProfit * HamBatches + RibProfit * PorkRibBatches, gp.GRB.MAXIMIZE)

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
