import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_184/data.json", "r") as f:
    data = json.load(f)

HorsesPerMediumCart = data["HorsesPerMediumCart"] # scalar parameter
CapacityMediumCart = data["CapacityMediumCart"] # scalar parameter
HorsesPerLargeCart = data["HorsesPerLargeCart"] # scalar parameter
CapacityLargeCart = data["CapacityLargeCart"] # scalar parameter
TotalHorses = data["TotalHorses"] # scalar parameter
MinimumMediumCarts = data["MinimumMediumCarts"] # scalar parameter
MinimumLargeCarts = data["MinimumLargeCarts"] # scalar parameter
CartRatio = data["CartRatio"] # scalar parameter
NumberOfMediumCarts = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfMediumCarts")
NumberOfLargeCarts = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfLargeCarts")

# Add non-negativity constraint for the number of medium sized carts
model.addConstr(NumberOfMediumCarts >= 0, name="non_negativity_medium_carts")

# The number of large sized carts should already be non-negative due to the variable type being integer,
# but we can also add a constraint for clarity.
model.addConstr(NumberOfLargeCarts >= 0, name="non_negativity_large_carts")

# Ensure total number of horses used by all carts does not exceed available horses
model.addConstr(HorsesPerMediumCart * NumberOfMediumCarts + HorsesPerLargeCart * NumberOfLargeCarts <= TotalHorses, "TotalHorsesConstraint")

# Set the number of medium carts to be equal to CartRatio times the number of large carts
model.addConstr(NumberOfMediumCarts == CartRatio * NumberOfLargeCarts, name="medium_large_cart_ratio")

model.addConstr(NumberOfMediumCarts >= MinimumMediumCarts, name="min_medium_carts")

model.addConstr(NumberOfLargeCarts >= MinimumLargeCarts, name="min_large_carts")

# Ensure that the total number of horses used does not exceed the available horses
model.addConstr(HorsesPerMediumCart * NumberOfMediumCarts + HorsesPerLargeCart * NumberOfLargeCarts <= TotalHorses, "horse_limit_constraint")

# Ensure that the number of medium carts meets at least the minimum required
model.addConstr(NumberOfMediumCarts >= MinimumMediumCarts, name="min_medium_carts")

# Ensure that the number of large carts meets at least the minimum required
model.addConstr(NumberOfLargeCarts >= MinimumLargeCarts, name="min_large_carts")

# Maintain the ratio of the number of medium carts to the number of large carts
model.addConstr(NumberOfMediumCarts <= CartRatio * NumberOfLargeCarts, name="MediumToLargeCartRatio")

# Set objective
model.setObjective(CapacityMediumCart * NumberOfMediumCarts + CapacityLargeCart * NumberOfLargeCarts, gp.GRB.MAXIMIZE)

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
