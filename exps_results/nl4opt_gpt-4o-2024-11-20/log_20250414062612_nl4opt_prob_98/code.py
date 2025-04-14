import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_98/data.json", "r") as f:
    data = json.load(f)

VintageVolume = data["VintageVolume"] # scalar parameter
RegularVolume = data["RegularVolume"] # scalar parameter
TotalVolume = data["TotalVolume"] # scalar parameter
MinRegularVintageRatio = data["MinRegularVintageRatio"] # scalar parameter
MinVintageBottles = data["MinVintageBottles"] # scalar parameter
VintageBottles = model.addVar(vtype=gp.GRB.CONTINUOUS, name="VintageBottles")
RegularBottles = model.addVar(vtype=gp.GRB.CONTINUOUS, name="RegularBottles")

# Add constraint ensuring vintage bottles are non-negative
model.addConstr(VintageBottles >= 0, name="non_negative_vintage_bottles")

# Non-negativity constraint for RegularBottles is already ensured by its default lower bound (0 in gurobipy).

# Add constraint: The number of regular bottles must be at least MinRegularVintageRatio times the number of vintage bottles
model.addConstr(RegularBottles >= MinRegularVintageRatio * VintageBottles, name="min_regular_vintage_ratio")

# Add constraint to ensure at least MinVintageBottles vintage bottles are produced
model.addConstr(VintageBottles >= MinVintageBottles, name="min_vintage_bottles")

# Add constraint for total combined volume of all bottles
model.addConstr(VintageVolume * VintageBottles + RegularVolume * RegularBottles <= TotalVolume, name="total_volume_constraint")

# Non-negativity constraint for the VintageBottles variable
model.addConstr(VintageBottles >= 0, name="non_negative_vintage_bottles")

# Add constraint to ensure the number of regular bottles is at least the minimum ratio times the number of vintage bottles
model.addConstr(RegularBottles >= MinRegularVintageRatio * VintageBottles, name="regular_vintage_ratio")

# Add minimum vintage bottles constraint
model.addConstr(VintageBottles >= MinVintageBottles, name="min_vintage_bottles")

# Add total volume constraint
model.addConstr(
    VintageVolume * VintageBottles + RegularVolume * RegularBottles <= TotalVolume,
    name="total_volume_constraint"
)

# Add constraint ensuring the number of regular bottles is at least the specified multiple of vintage bottles
model.addConstr(RegularBottles >= MinRegularVintageRatio * VintageBottles, name="regular_vintage_ratio")

# Add constraint to ensure the number of vintage bottles meets the minimum requirement
model.addConstr(VintageBottles >= MinVintageBottles, name="min_vintage_bottles")

# Set objective
model.setObjective(VintageBottles + RegularBottles, gp.GRB.MAXIMIZE)

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
