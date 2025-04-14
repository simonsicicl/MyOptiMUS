import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_265/data.json", "r") as f:
    data = json.load(f)

GolfCartCapacity = data["GolfCartCapacity"] # scalar parameter
PullCartCapacity = data["PullCartCapacity"] # scalar parameter
MaxGolfCartProportion = data["MaxGolfCartProportion"] # scalar parameter
MinGuests = data["MinGuests"] # scalar parameter
TotalGolfCarts = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalGolfCarts")
TotalPullCarts = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalPullCarts")

# Add constraint for golf cart count to be non-negative
model.addConstr(TotalGolfCarts >= 0, name="non_negative_golfcarts")

# Since the TotalPullCarts variable is defined with non-negativity by default in Gurobi (continuous variables have their lower bound set to 0), no additional constraint needs to be added.

# Add constraint to limit the proportion of golf carts to MaxGolfCartProportion
model.addConstr((1 - MaxGolfCartProportion) * TotalGolfCarts <= MaxGolfCartProportion * TotalPullCarts, name="golf_cart_proportion_limit")

# Add transportation capacity constraint to meet or exceed the minimum guest requirement
model.addConstr(
    TotalGolfCarts * GolfCartCapacity + TotalPullCarts * PullCartCapacity >= MinGuests,
    name="min_guest_transport"
)

# Add constraint to meet the minimum guest transportation requirement
model.addConstr(
    TotalGolfCarts * GolfCartCapacity + TotalPullCarts * PullCartCapacity >= MinGuests,
    name="min_guest_transportation"
)

# Add constraint to ensure the proportion of golf carts does not exceed the maximum allowed proportion of the total carts
model.addConstr(
    TotalGolfCarts <= MaxGolfCartProportion * (TotalGolfCarts + TotalPullCarts),
    name="max_golf_cart_proportion"
)

# Add non-negativity constraint for TotalPullCarts
model.addConstr(TotalPullCarts >= 0, name="non_negative_ToolPullCarts")

# Add constraint to ensure the minimum number of guests transported is satisfied
model.addConstr(
    GolfCartCapacity * TotalGolfCarts + PullCartCapacity * TotalPullCarts >= MinGuests, 
    name="min_guests_transported"
)

# Add constraint to limit the maximum proportion of golf carts relative to the total number of carts
model.addConstr(TotalGolfCarts <= MaxGolfCartProportion * (TotalGolfCarts + TotalPullCarts), name="max_golf_cart_proportion")

# Add non-negativity constraints for the number of carts
model.addConstr(TotalGolfCarts >= 0, name="non_negative_golf_carts")
model.addConstr(TotalPullCarts >= 0, name="non_negative_pull_carts")

# Set objective
model.setObjective(TotalGolfCarts + TotalPullCarts, gp.GRB.MINIMIZE)

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
