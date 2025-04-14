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
NumberOfSmallSuitcases = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfSmallSuitcases")
NumberOfLargeSuitcases = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfLargeSuitcases")

# Since NumberOfSmallSuitcases is already required to be integer, the non-negativity constraint is inherent.
model.addConstr(NumberOfSmallSuitcases >= 0, name="non_negativity_small_suitcases")

# Add constraint to ensure the number of large suitcases is non-negative
model.addConstr(NumberOfLargeSuitcases >= 0, "non_negativity_large_suitcases")

# Constraint for the number of small suitcases to be at least RatioSmallToLarge times as many as large suitcases
model.addConstr(NumberOfSmallSuitcases >= RatioSmallToLarge * NumberOfLargeSuitcases, "RatioSmallLargeSuitcases")

# Add constraint reflecting the maximum number of small suitcases available
model.addConstr(NumberOfSmallSuitcases <= MaxSmallSuitcases, name="max_small_suitcases")

# Constraint for the maximum number of large suitcases available
model.addConstr(NumberOfLargeSuitcases <= MaxLargeSuitcases, name="max_large_suitcases")

# Add constraint for minimum number of large suitcases
model.addConstr(NumberOfLargeSuitcases >= MinLargeSuitcases, name="min_large_suitcases_constraint")

# Add constraint to ensure the total number of small and large suitcases does not exceed the maximum allowed
model.addConstr(NumberOfSmallSuitcases + NumberOfLargeSuitcases <= MaxTotalSuitcases, "total_suitcases_constraint")

# Add constraint to maintain the minimum ratio of small to large suitcases
model.addConstr(NumberOfSmallSuitcases >= RatioSmallToLarge * NumberOfLargeSuitcases, name="min_ratio_small_to_large_suitcases")

# Add constraint to ensure the number of small suitcases does not exceed the maximum available
model.addConstr(NumberOfSmallSuitcases <= MaxSmallSuitcases, "max_small_suitcases_constraint")

# Add constraint to ensure the number of large suitcases does not exceed the maximum available
model.addConstr(NumberOfLargeSuitcases <= MaxLargeSuitcases, "max_large_suitcases_constraint")

# Ensure the minimum number of large suitcases constraint is respected
model.addConstr(NumberOfLargeSuitcases >= MinLargeSuitcases, name="min_large_suitcases")

# Add constraint to not exceed the maximum total number of suitcases that can be sent
model.addConstr(NumberOfSmallSuitcases + NumberOfLargeSuitcases <= MaxTotalSuitcases, name="max_total_suitcases_constraint")

# Define the objective function
model.setObjective(SmallCapacity * NumberOfSmallSuitcases + LargeCapacity * NumberOfLargeSuitcases, gp.GRB.MAXIMIZE)

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
