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
NumberOfSmallBottles = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfSmallBottles")
NumberOfLargeBottles = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfLargeBottles")

# The NumberOfSmallBottles variable is already defined as non-negative and integer in its code.

# No additional code needed since the variable NumberOfLargeBottles is already defined to be non-negative and integer

# Constraint for limiting the number of small bottles used to MaxSmallBottles
model.addConstr(NumberOfSmallBottles <= MaxSmallBottles, name="max_small_bottles_constraint")

# Add constraint for the maximum number of large bottles available
model.addConstr(NumberOfLargeBottles <= MaxLargeBottles, name="max_large_bottles")

# At least MinRatioSmallToLarge times as many small bottles must be used as large bottles
model.addConstr(NumberOfSmallBottles >= MinRatioSmallToLarge * NumberOfLargeBottles, name="min_ratio_small_to_large_bottles")

# Constraint for maximum number of bottles transported
model.addConstr(NumberOfSmallBottles + NumberOfLargeBottles <= MaxBottlesTransported, 
                name="max_bottles_transported")

# At least MinLargeBottles must be large bottles
model.addConstr(NumberOfLargeBottles >= MinLargeBottles, name="min_large_bottles_constraint")

# Constraint: Number of small and large bottles transported should not exceed the maximum number
model.addConstr(NumberOfSmallBottles + NumberOfLargeBottles <= MaxBottlesTransported, "max_bottles_constraint")

# Ensure that the number of small bottles does not exceed the maximum available
model.addConstr(NumberOfSmallBottles <= MaxSmallBottles, name="small_bottles_limit")

# Ensure that the number of large bottles does not exceed the maximum available
model.addConstr(NumberOfLargeBottles <= MaxLargeBottles, name="max_large_bottles_constraint")

# Ensure the number of large bottles meets the minimum requirement
model.addConstr(NumberOfLargeBottles >= MinLargeBottles, name="min_large_bottles_constraint")

# Add constraint to maintain the minimum ratio of the number of small bottles to large bottles
model.addConstr(NumberOfSmallBottles >= MinRatioSmallToLarge * NumberOfLargeBottles, name="min_ratio_small_to_large_bottles")

# Define the objective function
model.setObjective(NumberOfSmallBottles * SmallBottleCapacity + NumberOfLargeBottles * LargeBottleCapacity, gp.GRB.MAXIMIZE)

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
