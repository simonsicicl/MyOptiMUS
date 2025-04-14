import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_167/data.json", "r") as f:
    data = json.load(f)

SmallWagonCapacity = data["SmallWagonCapacity"] # scalar parameter
LargeWagonCapacity = data["LargeWagonCapacity"] # scalar parameter
MinRatioSmallToLarge = data["MinRatioSmallToLarge"] # scalar parameter
MinLargeWagons = data["MinLargeWagons"] # scalar parameter
TotalOre = data["TotalOre"] # scalar parameter
NumberOfSmallWagons = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfSmallWagons")
NumberOfLargeWagons = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfLargeWagons")

# Since NumberOfSmallWagons has already been defined as an integer variable, 
# the non-negativity constraint is implicitly enforced by the variable type. 
# No additional constraints required.

# Since NumberOfLargeWagons has already been defined as an integer variable, 
# we just need to add a constraint to ensure it is non-negative.
model.addConstr(NumberOfLargeWagons >= 0, "NumberOfLargeWagons_nonneg")



# Ensure that at least MinLargeWagons large wagons are used
model.addConstr(NumberOfLargeWagons >= MinLargeWagons, name="min_large_wagons_constraint")

# Total ore transportation constraint
model.addConstr((NumberOfSmallWagons * SmallWagonCapacity) + (NumberOfLargeWagons * LargeWagonCapacity) == TotalOre, name="total_ore_transportation")

# Ensure that the capacity of small and large wagons can carry all the ore
model.addConstr((NumberOfSmallWagons * SmallWagonCapacity) + (NumberOfLargeWagons * LargeWagonCapacity) >= TotalOre, name="wagons_capacity_constraint")

# Maintain the minimum ratio of small to large wagons
model.addConstr(NumberOfSmallWagons >= MinRatioSmallToLarge * NumberOfLargeWagons, name="min_small_to_large_ratio")

# Ensure that the minimum number of large wagons is used
model.addConstr(NumberOfLargeWagons >= MinLargeWagons, name="min_large_wagons")

# Define the objective function
model.setObjective(NumberOfSmallWagons + NumberOfLargeWagons, gp.GRB.MINIMIZE)

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
