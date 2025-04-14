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
SmallBouquets = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SmallBouquets")
LargeBouquets = model.addVar(vtype=gp.GRB.CONTINUOUS, name="LargeBouquets")

# The variable "SmallBouquets" already has a non-negativity constraint automatically applied because it is defined as a continuous Gurobi variable (which defaults to having a lower bound of 0). No additional constraint needs to be explicitly added.

# The variable "LargeBouquets" already has non-negativity enforced internally due to its default non-negative domain in Gurobi,
# so no additional constraint code is required.

# Add constraint for maximum number of small bouquets that can be transported
model.addConstr(SmallBouquets <= MaxSmallBouquets, name="max_small_bouquets")

# Add constraint for maximum number of large bouquets that can be transported
model.addConstr(LargeBouquets <= MaxLargeBouquets, name="max_large_bouquets")

# Add constraint for the total number of bouquets
model.addConstr(SmallBouquets + LargeBouquets <= MaxTotalBouquets, name="total_bouquets_limit")

# Add constraint to ensure at least MinLargeBouquets large bouquets are transported
model.addConstr(LargeBouquets >= MinLargeBouquets, name="min_large_bouquets")

# Add constraint to ensure SmallBouquets is at least MinSmallLargeRatio times LargeBouquets
model.addConstr(SmallBouquets >= MinSmallLargeRatio * LargeBouquets, name="min_small_large_ratio")

# Add constraint for maximum number of small bouquets
model.addConstr(SmallBouquets <= MaxSmallBouquets, name="max_small_bouquets_constraint")

# Add constraint for maximum number of large bouquets
model.addConstr(LargeBouquets <= MaxLargeBouquets, name="max_large_bouquets")

# Add constraint for the maximum number of bouquets transported
model.addConstr(SmallBouquets + LargeBouquets <= MaxTotalBouquets, name="max_bouquets_limit")

# Add constraint to ensure the number of large bouquets meets the minimum requirement
model.addConstr(LargeBouquets >= MinLargeBouquets, name="min_large_bouquets")

# Add constraint to ensure the ratio of small bouquets to large bouquets meets the specified minimum
model.addConstr(SmallBouquets >= MinSmallLargeRatio * LargeBouquets, name="min_small_large_ratio")

# Set objective
model.setObjective(SmallBouquets * SmallBouquetSize + LargeBouquets * LargeBouquetSize, gp.GRB.MAXIMIZE)

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
