import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_285/data.json", "r") as f:
    data = json.load(f)

WideCapacity = data["WideCapacity"] # scalar parameter
NarrowCapacity = data["NarrowCapacity"] # scalar parameter
WideGarbage = data["WideGarbage"] # scalar parameter
NarrowGarbage = data["NarrowGarbage"] # scalar parameter
MaxWideTrails = data["MaxWideTrails"] # scalar parameter
MaxCapacity = data["MaxCapacity"] # scalar parameter
NumberOfWideTrails = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfWideTrails")
NumberOfNarrowTrails = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfNarrowTrails")

model.addConstr(NumberOfWideTrails >= 0, "NumberOfWideTrails_non_negative")

# Since NumberOfNarrowTrails is already guaranteed to be non-negative by its variable type,
# no additional constraint is necessary.

# Add constraint: Total visitors from wide trails does not exceed WideCapacity multiplied by the number of wide trails
model.addConstr(NumberOfWideTrails * WideCapacity <= MaxCapacity, "wide_trail_visitor_capacity")

# Add constraint for total visitors from narrow trails not exceeding the capacity
TotalVisitorsNarrowTrails = model.addVar(vtype=gp.GRB.INTEGER, name="TotalVisitorsNarrowTrails")
model.addConstr(TotalVisitorsNarrowTrails <= NarrowCapacity * NumberOfNarrowTrails, "TotalVisitorsNarrowTrails_limit")

# Add constraint to ensure the total number of wide trails does not exceed MaxWideTrails
model.addConstr(NumberOfWideTrails <= MaxWideTrails, "max_wide_trails_constraint")

# Park's total visitor capacity constraint
model.addConstr(NumberOfWideTrails * WideCapacity + NumberOfNarrowTrails * NarrowCapacity <= MaxCapacity, "ParkVisitorCapacity")

# No extra code required since variable NumberOfWideTrails is already defined as an integer

# No extra code required since variable NumberOfNarrowTrails is already declared as integer

# Total visitor capacity constraint for trails
model.addConstr((NumberOfWideTrails * WideCapacity) + (NumberOfNarrowTrails * NarrowCapacity) <= MaxCapacity, "total_visitor_capacity")

# Constraint: The number of wide trails must not exceed the maximum number of wide trails allowed
model.addConstr(NumberOfWideTrails <= MaxWideTrails, name="max_wide_trails_constraint")

# Set objective
model.setObjective(NumberOfWideTrails * WideGarbage + NumberOfNarrowTrails * NarrowGarbage, gp.GRB.MINIMIZE)

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
