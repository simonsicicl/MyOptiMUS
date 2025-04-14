import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_190/data.json", "r") as f:
    data = json.load(f)

SmallCrateCapacity = data["SmallCrateCapacity"] # scalar parameter
LargeCrateCapacity = data["LargeCrateCapacity"] # scalar parameter
SmallToLargeRatio = data["SmallToLargeRatio"] # scalar parameter
MaxSmallCrates = data["MaxSmallCrates"] # scalar parameter
MaxLargeCrates = data["MaxLargeCrates"] # scalar parameter
MaxTotalCrates = data["MaxTotalCrates"] # scalar parameter
MinLargeCrates = data["MinLargeCrates"] # scalar parameter
SmallCrates = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SmallCrates")
LargeCrates = model.addVar(vtype=gp.GRB.CONTINUOUS, name="LargeCrates")

# The variable SmallCrates is already defined as non-negative due to its default properties (continuous variables in Gurobi are non-negative unless stated otherwise); no additional constraint is needed.

# No additional code needed since the variable "LargeCrates" is already defined with non-negativity guaranteed by being a continuous variable in gurobipy.

# Add constraint for the minimum ratio of small crates to large crates
model.addConstr(SmallCrates >= SmallToLargeRatio * LargeCrates, name="min_small_to_large_crates_ratio")

# Add constraint ensuring the number of small crates used does not exceed the maximum limit
model.addConstr(SmallCrates <= MaxSmallCrates, name="max_small_crates_limit")

# Add constraint to ensure the number of large crates used does not exceed the maximum allowed
model.addConstr(LargeCrates <= MaxLargeCrates, name="max_large_crates_constraint")

# Add constraint for total number of crates
model.addConstr(SmallCrates + LargeCrates <= MaxTotalCrates, name="total_crates_constraint")

# Add constraint to ensure the number of large crates used meets the minimum requirement  
model.addConstr(LargeCrates >= MinLargeCrates, name="min_large_crates_requirement")

# Add constraint to ensure the minimum ratio of small crates to large crates
model.addConstr(SmallCrates >= SmallToLargeRatio * LargeCrates, name="min_ratio_small_large_crates")

# Add constraint to ensure the number of small crates does not exceed the maximum available
model.addConstr(SmallCrates <= MaxSmallCrates, name="max_small_crates_constraint")

# Add constraint to ensure the number of large crates does not exceed the maximum available
model.addConstr(LargeCrates <= MaxLargeCrates, name="max_large_crates_constraint")

# Add constraint to ensure the truck does not surpass its maximum total capacity of crates
model.addConstr(SmallCrates + LargeCrates <= MaxTotalCrates, name="truck_capacity")

# Add constraint to ensure the minimum number of large crates is used
model.addConstr(LargeCrates >= MinLargeCrates, name="min_large_crates_constraint")

# Set objective
model.setObjective((SmallCrates * SmallCrateCapacity) + (LargeCrates * LargeCrateCapacity), gp.GRB.MAXIMIZE)

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
