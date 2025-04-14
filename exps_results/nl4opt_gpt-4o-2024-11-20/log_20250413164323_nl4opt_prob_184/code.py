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
MediumCarts = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MediumCarts")
LargeCarts = model.addVar(vtype=gp.GRB.CONTINUOUS, name="LargeCarts")

# The variable MediumCarts is already defined as non-negative due to its default lower bound (0) in Gurobi.
# No additional constraint is needed for this requirement.

# No additional code needed since the variable "LargeCarts" is non-negative by default (continuous variables in Gurobi are non-negative unless otherwise specified).

# Add constraint to ensure total horses used do not exceed available horses
model.addConstr(
    HorsesPerMediumCart * MediumCarts + HorsesPerLargeCart * LargeCarts <= TotalHorses, 
    name="total_horses_limit"
)

# Add constraint ensuring the number of medium-sized carts equals CartRatio times the number of large-sized carts
model.addConstr(MediumCarts == CartRatio * LargeCarts, name="cart_ratio_constraint")

# Add constraint to enforce minimum usage of medium-sized carts
model.addConstr(MediumCarts >= MinimumMediumCarts, name="min_medium_carts")

# Ensure integer constraint on LargeCarts since the number of carts should be an integer
LargeCarts.vtype = gp.GRB.INTEGER

# Add minimum large cart constraint
model.addConstr(LargeCarts >= MinimumLargeCarts, name="min_large_carts")

# Add constraint to ensure the total number of horses used by all carts does not exceed the available number of horses
model.addConstr(HorsesPerMediumCart * MediumCarts + HorsesPerLargeCart * LargeCarts <= TotalHorses, name="horse_availability")

# Add constraint to ensure the number of medium-sized carts is at least the minimum required
model.addConstr(MediumCarts >= MinimumMediumCarts, name="min_medium_carts")

# Add constraint to ensure the number of large-sized carts is at least the minimum required
model.addConstr(LargeCarts >= MinimumLargeCarts, name="min_large_carts")

# Add constraint to enforce the ratio of medium-sized carts to large-sized carts
model.addConstr(MediumCarts == CartRatio * LargeCarts, name="medium_to_large_ratio")

# Set objective
model.setObjective(CapacityMediumCart * MediumCarts + CapacityLargeCart * LargeCarts, gp.GRB.MAXIMIZE)

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
