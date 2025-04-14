import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_160/data.json", "r") as f:
    data = json.load(f)

SmallBouquetSize = data["SmallBouquetSize"] # scalar parameter
LargeBouquetSize = data["LargeBouquetSize"] # scalar parameter
MaxSmallBouquets = data["MaxSmallBouquets"] # scalar parameter
MaxLargeBouquets = data["MaxLargeBouquets"] # scalar parameter
MaxTotalBouquets = data["MaxTotalBouquets"] # scalar parameter
MinLargeBouquets = data["MinLargeBouquets"] # scalar parameter
MinSmallLargeRatio = data["MinSmallLargeRatio"] # scalar parameter
NumSmallBouquets = model.addVar(vtype=gp.GRB.INTEGER, name="NumSmallBouquets")
NumLargeBouquets = model.addVar(vtype=gp.GRB.INTEGER, name="NumLargeBouquets")

# Since x_{Small} is a variable, its non-negativity is usually ensured by its variable type setting.
# If there is no need to add an explicit constraint, the non-negativity should be inherent to the variable definition.
# Hence, no additional code is required for this constraint.

model.addConstr(NumLargeBouquets >= 0, name="non_negativity_large_bouquets")

# At most, the maximum number of small bouquets can be transported
model.addConstr(NumSmallBouquets <= MaxSmallBouquets, name="Max_Small_Bouquets")

# At most MaxLargeBouquets large bouquets can be transported
model.addConstr(NumLargeBouquets <= MaxLargeBouquets, name="MaxLargeBouquets_constraint")

# Add constraint for the maximum total number of bouquets that can be transported
model.addConstr(NumSmallBouquets + NumLargeBouquets <= MaxTotalBouquets, name="max_total_bouquets")

# At least MinLargeBouquets large bouquets must be transported
model.addConstr(NumLargeBouquets >= MinLargeBouquets, name="min_large_bouquets")

# The number of small bouquets must be at least MinSmallLargeRatio times the number of large bouquets
model.addConstr(NumSmallBouquets >= MinSmallLargeRatio * NumLargeBouquets, name="small_to_large_bouquet_ratio")

# Add constraint for the minimum ratio of small to large bouquets
model.addConstr(NumSmallBouquets >= MinSmallLargeRatio * NumLargeBouquets, name="small_to_large_ratio")

# Maximum transport capacity constraint for small bouquets
model.addConstr(NumSmallBouquets <= MaxSmallBouquets, name="max_small_bouquets")

model.addConstr(NumLargeBouquets <= MaxLargeBouquets, name="max_large_bouquets_capacity")

# Add constraint for the total number of bouquets not exceeding maximum transport capacity
model.addConstr(NumSmallBouquets + NumLargeBouquets <= MaxTotalBouquets, "capacity_constraint")

# Minimum large bouquets constraint
model.addConstr(NumLargeBouquets >= MinLargeBouquets, name="min_large_bouquets")

# Set objective
model.setObjective(SmallBouquetSize * NumSmallBouquets + LargeBouquetSize * NumLargeBouquets, gp.GRB.MAXIMIZE)

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
