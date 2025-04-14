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
NumberOfSmallCrates = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfSmallCrates")
NumberOfLargeCrates = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfLargeCrates")

# Constraint: Number of small crates must be non-negative
model.addConstr(NumberOfSmallCrates >= 0, name="non_negative_small_crates")

# Constraint: Number of large crates used for transporting grapes must be non-negative
model.addConstr(NumberOfLargeCrates >= 0, name="non_negative_large_crates")

# Add constraint for small crates to be at least SmallToLargeRatio times the number of large crates
model.addConstr(NumberOfSmallCrates >= SmallToLargeRatio * NumberOfLargeCrates, name="SmallToLargeRatio_Constraint")

model.addConstr(NumberOfSmallCrates <= MaxSmallCrates, name="max_small_crates")

# Constraint: Number of large crates used cannot exceed the maximum available
model.addConstr(NumberOfLargeCrates <= MaxLargeCrates, name="large_crates_limit")

# Constraint for the maximum total number of crates the truck can take
model.addConstr(NumberOfSmallCrates + NumberOfLargeCrates <= MaxTotalCrates, name="max_total_crates")

# At least MinLargeCrates large crates must be used constraint
model.addConstr(NumberOfLargeCrates >= MinLargeCrates, name="min_large_crates")

# Add constraint: Number of small crates should be at least three times the number of large crates
model.addConstr(NumberOfSmallCrates >= 3 * NumberOfLargeCrates, "min_small_to_large_crates_ratio")

model.addConstr(NumberOfSmallCrates <= MaxSmallCrates, name="small_crates_limit")

model.addConstr(NumberOfLargeCrates <= MaxLargeCrates, name="large_crates_limit")

# Constraint: The total number of crates on the truck cannot exceed the truck's capacity
model.addConstr(NumberOfSmallCrates + NumberOfLargeCrates <= MaxTotalCrates, "truck_capacity_constraint")

# Add constraint for the minimum number of large crates
model.addConstr(NumberOfLargeCrates >= MinLargeCrates, name="min_large_crates")

# Define the objective function
model.setObjective(NumberOfSmallCrates * SmallCrateCapacity + NumberOfLargeCrates * LargeCrateCapacity, gp.GRB.MAXIMIZE)

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
