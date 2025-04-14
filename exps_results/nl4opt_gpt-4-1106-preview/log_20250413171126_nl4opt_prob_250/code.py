import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_250/data.json", "r") as f:
    data = json.load(f)

CanVolume = data["CanVolume"] # scalar parameter
BottleVolume = data["BottleVolume"] # scalar parameter
MinTotalVolume = data["MinTotalVolume"] # scalar parameter
CanBottleRatio = data["CanBottleRatio"] # scalar parameter
MinBottles = data["MinBottles"] # scalar parameter
NumberOfCans = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfCans")
NumberOfBottles = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfBottles")

# Add constraint to ensure the number of cans produced is non-negative
model.addConstr(NumberOfCans >= 0, name="cans_non_negative")

# Constraint to ensure the number of glass bottles is non-negative
model.addConstr(NumberOfBottles >= 0, name="non_negative_bottles")

# Total volume from cans and bottles must be at least the minimum required total volume
model.addConstr(NumberOfCans * CanVolume + NumberOfBottles * BottleVolume >= MinTotalVolume, name="min_total_volume")

# Add constraint: The number of cans must be at least CanBottleRatio times greater than the number of glass bottles
model.addConstr(NumberOfCans >= CanBottleRatio * NumberOfBottles, name="cans_to_bottles_ratio")

# Add constraint to ensure the minimum number of bottles produced
model.addConstr(NumberOfBottles >= MinBottles, "min_bottles_produced")

# Set objective
model.setObjective(NumberOfCans + NumberOfBottles, gp.GRB.MAXIMIZE)

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
