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
GolfCarts = model.addVar(vtype=gp.GRB.INTEGER, name="GolfCarts")
PullCarts = model.addVar(vtype=gp.GRB.INTEGER, name="PullCarts")

# The number of golf carts must be non-negative
model.addConstr(GolfCarts >= 0, name="golf_carts_nonnegativity")

# Since PullCarts has already been added as an integer variable, we only need to set the constraint that it must be non-negative.
model.addConstr(PullCarts >= 0, name="non_negative_pull_carts")

# Add constraint: At most MaxGolfCartProportion of the total number of carts can be golf carts
model.addConstr(GolfCarts <= MaxGolfCartProportion * (GolfCarts + PullCarts), "max_golf_cart_proportion")

# Ensure that at least the minimum number of guests can be transported
model.addConstr(GolfCarts * GolfCartCapacity + PullCarts * PullCartCapacity >= MinGuests, name="min_guests_transport")

# Ensure the minimum number of guests can be transported
model.addConstr((GolfCartCapacity * GolfCarts) + (PullCartCapacity * PullCarts) >= MinGuests, name="min_guests_transport")

# Add constraint to limit the number of golf carts based on the maximum proportion
model.addConstr(GolfCarts <= MaxGolfCartProportion * (GolfCarts + PullCarts), name="max_golf_cart_proportion")

# Set objective
model.setObjective(GolfCarts + PullCarts, gp.GRB.MINIMIZE)

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
