import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_150/data.json", "r") as f:
    data = json.load(f)

SmallBottleCapacity = data["SmallBottleCapacity"] # scalar parameter
LargeBottleCapacity = data["LargeBottleCapacity"] # scalar parameter
MaxSmallBottles = data["MaxSmallBottles"] # scalar parameter
MaxLargeBottles = data["MaxLargeBottles"] # scalar parameter
MaxBottlesTransported = data["MaxBottlesTransported"] # scalar parameter
MinRatioSmallToLarge = data["MinRatioSmallToLarge"] # scalar parameter
MinLargeBottles = data["MinLargeBottles"] # scalar parameter
SmallBottlesUsed = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SmallBottlesUsed")
LargeBottlesUsed = model.addVar(vtype=gp.GRB.CONTINUOUS, name="LargeBottlesUsed")

# Update SmallBottlesUsed variable's type to integer and ensure non-negativity
SmallBottlesUsed.vtype = gp.GRB.INTEGER
SmallBottlesUsed.LB = 0

# Since the variable "LargeBottlesUsed" is defined as a continuous variable, we need to adjust its type to integer to satisfy the requirement
LargeBottlesUsed.vtype = gp.GRB.INTEGER

# Add constraint to ensure the number of small bottles used does not exceed the maximum available
model.addConstr(SmallBottlesUsed <= MaxSmallBottles, name="max_small_bottles_constraint")

# Add constraint to ensure the number of large bottles used does not exceed the maximum allowed
model.addConstr(LargeBottlesUsed <= MaxLargeBottles, name="large_bottles_limit")

# Add constraint for minimum ratio of small bottles to large bottles
model.addConstr(SmallBottlesUsed >= MinRatioSmallToLarge * LargeBottlesUsed, name="min_ratio_small_to_large")

# Add constraint to limit the total number of bottles transported
model.addConstr(SmallBottlesUsed + LargeBottlesUsed <= MaxBottlesTransported, name="MaxBottlesConstraint")

# Add constraint for the minimum number of large bottles used
model.addConstr(LargeBottlesUsed >= MinLargeBottles, name="min_large_bottles_constraint")

# LargeBottlesUsed must take an integer value
LargeBottlesUsed.vtype = gp.GRB.INTEGER

# Add constraint ensuring the number of small bottles used does not exceed the maximum available
model.addConstr(SmallBottlesUsed <= MaxSmallBottles, name="small_bottles_limit")

# Add constraint ensuring the number of large bottles used does not exceed the maximum available
model.addConstr(LargeBottlesUsed <= MaxLargeBottles, name="large_bottles_limit")

# Add constraint for maximum number of bottles transported
model.addConstr(SmallBottlesUsed + LargeBottlesUsed <= MaxBottlesTransported, name="max_bottles_transport")

# Add constraint to maintain the minimum ratio between small and large bottles
model.addConstr(SmallBottlesUsed >= MinRatioSmallToLarge * LargeBottlesUsed, name="min_ratio_small_to_large")

# Add constraint to ensure at least the minimum number of large bottles are used
model.addConstr(LargeBottlesUsed >= MinLargeBottles, name="min_large_bottles")

# Set objective
model.setObjective(SmallBottleCapacity * SmallBottlesUsed + LargeBottleCapacity * LargeBottlesUsed, gp.GRB.MAXIMIZE)

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
