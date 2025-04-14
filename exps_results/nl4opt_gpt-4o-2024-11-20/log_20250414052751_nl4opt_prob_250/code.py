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
NumCans = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumCans")
NumBottles = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumBottles")

# Add non-negativity constraints for production variables
model.addConstr(NumCans >= 0, name="non_negative_NumCans")
model.addConstr(NumBottles >= 0, name="non_negative_NumBottles")

# NumBottles is a continuous variable. Non-negativity is already ensured by default in Gurobi for continuous variables with no lower bounds explicitly set below zero.

# Add constraint for total soda volume from cans and bottles
model.addConstr(CanVolume * NumCans + BottleVolume * NumBottles >= MinTotalVolume, name="min_total_volume")

# Add constraint to ensure the number of cans is at least CanBottleRatio times the number of bottles
model.addConstr(NumCans >= CanBottleRatio * NumBottles, name="cans_bottles_ratio")

# Add constraint to ensure at least MinBottles glass bottles are produced
model.addConstr(NumBottles >= MinBottles, name="min_bottles_produced")

# Add minimum production constraint
model.addConstr(NumBottles >= MinBottles, name="min_glass_bottles")

# Total daily soda volume constraint
model.addConstr(NumCans * CanVolume + NumBottles * BottleVolume >= MinTotalVolume, 
                name="min_daily_soda_volume")

# Add minimum ratio constraint between NumCans and NumBottles
model.addConstr(NumCans >= CanBottleRatio * NumBottles, name="min_can_bottle_ratio")

# Add constraint to ensure daily minimum volume requirement is met
model.addConstr(
    NumCans * CanVolume + NumBottles * BottleVolume >= MinTotalVolume,
    name="min_volume_requirement"
)

# Add constraint to ensure the number of soda cans produced is at least the specified multiple of the number of bottles produced
model.addConstr(NumCans >= CanBottleRatio * NumBottles, name="can_bottle_ratio_constraint")

# Add minimum production constraint for glass bottles
model.addConstr(NumBottles >= MinBottles, name="min_bottles_production")

# Set objective
model.setObjective(NumCans + NumBottles, gp.GRB.MAXIMIZE)

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
