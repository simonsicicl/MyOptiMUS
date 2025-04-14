import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_170/data.json", "r") as f:
    data = json.load(f)

SmallCapacity = data["SmallCapacity"] # scalar parameter
LargeCapacity = data["LargeCapacity"] # scalar parameter
RatioSmallToLarge = data["RatioSmallToLarge"] # scalar parameter
MaxSmallSuitcases = data["MaxSmallSuitcases"] # scalar parameter
MaxLargeSuitcases = data["MaxLargeSuitcases"] # scalar parameter
MinLargeSuitcases = data["MinLargeSuitcases"] # scalar parameter
MaxTotalSuitcases = data["MaxTotalSuitcases"] # scalar parameter
NumSmallSuitcases = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumSmallSuitcases")
NumLargeSuitcases = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumLargeSuitcases")

# Ensure the number of small suitcases sent is non-negative
model.addConstr(NumSmallSuitcases >= 0, name="non_negative_NumSmallSuitcases")

# No additional code is necessary as the non-negativity constraint is automatically handled by Gurobi for non-negative domain variables such as NumLargeSuitcases, which is defined as CONTINUOUS and not restricted to negative values.

# Add constraint for the relationship between small and large suitcases
model.addConstr(NumSmallSuitcases >= RatioSmallToLarge * NumLargeSuitcases, name="small_large_suitcase_ratio")

# Add constraint for the total number of small suitcases
model.addConstr(NumSmallSuitcases <= MaxSmallSuitcases, name="max_small_suitcases")

# Add constraint to limit the number of large suitcases
model.addConstr(NumLargeSuitcases <= MaxLargeSuitcases, name="limit_large_suitcases")

# Add constraint to ensure at least MinLargeSuitcases large suitcases are sent
model.addConstr(NumLargeSuitcases >= MinLargeSuitcases, name="min_large_suitcases")

# Add constraint to ensure the total number of suitcases does not exceed the maximum allowed
model.addConstr(NumSmallSuitcases + NumLargeSuitcases <= MaxTotalSuitcases, name="total_suitcase_limit")

# Add constraint to ensure the number of small suitcases sent does not exceed the maximum available
model.addConstr(NumSmallSuitcases <= MaxSmallSuitcases, name="max_small_suitcases_constraint")

# Add constraint to ensure the number of large suitcases sent does not exceed the maximum available
model.addConstr(NumLargeSuitcases <= MaxLargeSuitcases, name="large_suitcase_limit")

# Add constraint to ensure a minimum number of large suitcases must be sent
model.addConstr(NumLargeSuitcases >= MinLargeSuitcases, name="min_large_suitcases")

# Add constraint to ensure total suitcases do not exceed the maximum allowed
model.addConstr(NumSmallSuitcases + NumLargeSuitcases <= MaxTotalSuitcases, name="total_suitcases_limit")

# Add constraint ensuring the ratio of small to large suitcases
model.addConstr(NumSmallSuitcases >= RatioSmallToLarge * NumLargeSuitcases, name="small_to_large_ratio")

# Set objective
model.setObjective(SmallCapacity * NumSmallSuitcases + LargeCapacity * NumLargeSuitcases, gp.GRB.MAXIMIZE)

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
