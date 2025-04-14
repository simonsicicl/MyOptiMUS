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
NumberOfVintageBottles = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfVintageBottles")
NumberOfRegularBottles = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfRegularBottles")

# Since NumberOfVintageBottles is already defined as an integer variable, 
# we just need to add a constraint to ensure it is non-negative
model.addConstr(NumberOfVintageBottles >= 0, "vintage_bottles_nonnegativity")

model.addConstr(NumberOfRegularBottles >= 0, name="NumberOfRegularBottles_nonneg")

# Add constraint for minimum ratio of regular bottles to vintage bottles
model.addConstr(NumberOfRegularBottles >= MinRegularVintageRatio * NumberOfVintageBottles, name="min_regular_vintage_ratio")

# Ensure at least a minimum number of vintage bottles are produced
model.addConstr(NumberOfVintageBottles >= MinVintageBottles, name="min_vintage_bottles")

# Ensure the total volume of vintage and regular bottles does not exceed available volume
model.addConstr((VintageVolume * NumberOfVintageBottles) + (RegularVolume * NumberOfRegularBottles) <= TotalVolume, name="volume_constraint")

# Add constraint for the number of regular bottles to be at least 4 times the number of vintage bottles
model.addConstr(NumberOfRegularBottles >= MinRegularVintageRatio * NumberOfVintageBottles, "min_ratio_regular_vintage")

# Ensure minimum production of vintage bottles
model.addConstr(NumberOfVintageBottles >= MinVintageBottles, name="min_vintage_production")

# Ensure that the volume constraints are respected for the vintage and regular bottles
model.addConstr(VintageVolume * NumberOfVintageBottles + RegularVolume * NumberOfRegularBottles <= TotalVolume, name="volume_constraint")

# Add constraint to maintain at least a minimum ratio of regular to vintage bottles produced
model.addConstr(NumberOfRegularBottles >= MinRegularVintageRatio * NumberOfVintageBottles, name="MinRegularVintageRatioConstraint")

# Ensure a minimum production of vintage bottles constraint
model.addConstr(NumberOfVintageBottles >= MinVintageBottles, name="min_vintage_production")

# Set objective
model.setObjective(NumberOfVintageBottles + NumberOfRegularBottles, gp.GRB.MAXIMIZE)

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
