import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_161/data.json", "r") as f:
    data = json.load(f)

GiftsNew = data["GiftsNew"] # scalar parameter
GiftsOld = data["GiftsOld"] # scalar parameter
DieselNew = data["DieselNew"] # scalar parameter
DieselOld = data["DieselOld"] # scalar parameter
MinGifts = data["MinGifts"] # scalar parameter
MaxTripsNew = data["MaxTripsNew"] # scalar parameter
MinPercentOld = data["MinPercentOld"] # scalar parameter
TripsNew = model.addVar(vtype=gp.GRB.INTEGER, name="TripsNew")
TripsOld = model.addVar(vtype=gp.GRB.INTEGER, name="TripsOld")

# Add constraint to ensure the number of trips by the new company is non-negative
model.addConstr(TripsNew >= 0, name="non_negative_trips_new")

# Constraint: The number of trips by the old company must be non-negative
model.addConstr(TripsOld >= 0, name="non_negativity_TripsOld")

# Add a constraint for the minimum number of gifts to be delivered
model.addConstr(GiftsNew * TripsNew + GiftsOld * TripsOld >= MinGifts, name="min_gifts_delivery")

# Constraint for the maximum number of trips by the new company
model.addConstr(TripsNew <= MaxTripsNew, "max_trips_new")

# Add constraint to ensure that at least MinPercentOld percent of all trips are made by the old company
model.addConstr(TripsOld >= MinPercentOld * (TripsOld + TripsNew), name="min_percent_old_trips")

# Ensure minimum total number of gifts constraint
model.addConstr(GiftsNew * TripsNew + GiftsOld * TripsOld >= MinGifts, name="MinGiftsDelivered")

model.addConstr(TripsNew <= MaxTripsNew, name="max_trips_new_constraint")

# Ensure at least a minimum percentage of trips are made by the old company
model.addConstr(TripsOld >= MinPercentOld * (TripsOld + TripsNew), name="min_percentage_old_company")

# Define objective function
objective = DieselNew * TripsNew + DieselOld * TripsOld

# Set the objective in the model
model.setObjective(objective, gp.GRB.MINIMIZE)

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
