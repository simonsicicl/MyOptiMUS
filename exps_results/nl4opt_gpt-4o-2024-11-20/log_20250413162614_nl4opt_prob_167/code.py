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
NumberOfSmallWagons = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfSmallWagons")
NumberOfLargeWagons = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfLargeWagons")

# The non-negativity is inherent due to the variable being declared as continuous.
# Constraint code not needed.

# The non-negativity constraint is inherently satisfied as the variable "NumberOfLargeWagons" is defined with type CONTINUOUS, which is non-negative by default.

# Add constraint to ensure the number of small wagons is at least MinRatioSmallToLarge times the number of large wagons
model.addConstr(NumberOfSmallWagons >= MinRatioSmallToLarge * NumberOfLargeWagons, name="min_ratio_small_to_large")

# Add constraint ensuring the number of large wagons used meets or exceeds the minimum required
model.addConstr(NumberOfLargeWagons >= MinLargeWagons, name="min_large_wagons")

# Add constraint ensuring total ore transported matches the required total ore
model.addConstr(
    NumberOfSmallWagons * SmallWagonCapacity + NumberOfLargeWagons * LargeWagonCapacity == TotalOre, 
    name="total_ore_constraint"
)

# Add constraint to ensure the number of small wagons is at least the minimum ratio times the number of large wagons
model.addConstr(NumberOfSmallWagons >= MinRatioSmallToLarge * NumberOfLargeWagons, name="MinRatioSmallToLargeConstraint")

# Enforce the minimum required number of large wagons constraint
model.addConstr(NumberOfLargeWagons >= MinLargeWagons, name="min_large_wagons_constraint")

# Add constraint to ensure the total ore transported meets or exceeds the demand
model.addConstr(SmallWagonCapacity * NumberOfSmallWagons + LargeWagonCapacity * NumberOfLargeWagons >= TotalOre, name="ore_transport_demand")

# Add constraint to maintain the minimum ratio of small wagons to large wagons
model.addConstr(NumberOfSmallWagons >= MinRatioSmallToLarge * NumberOfLargeWagons, name="min_ratio_small_to_large")

# Add constraint to ensure the minimum number of large wagons is met
model.addConstr(NumberOfLargeWagons >= MinLargeWagons, name="min_large_wagons")

# Set objective
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
