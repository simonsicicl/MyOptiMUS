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
TripsNew = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TripsNew")
TripsOld = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TripsOld")

# The variable TripsNew already has the non-negativity constraint because it was defined as a continuous variable (default non-negative domain).

# Add non-negativity constraint for TripsOld
model.addConstr(TripsOld >= 0, name="non_negativity_TripsOld")

# Add constraint to ensure at least MinGifts are delivered
model.addConstr(TripsNew * GiftsNew + TripsOld * GiftsOld >= MinGifts, name="min_gifts_constraint")

# Add constraint ensuring the number of trips made by the new company does not exceed the maximum limit
model.addConstr(TripsNew <= MaxTripsNew, name="max_trips_new")

# Add the constraint to ensure at least MinPercentOld percent of all trips are made by the old company
model.addConstr(TripsOld >= (MinPercentOld / (1 - MinPercentOld)) * TripsNew, name="min_percent_old_constraint")

# Add constraint for minimum required gifts delivered
model.addConstr(TripsNew * GiftsNew + TripsOld * GiftsOld >= MinGifts, name="min_gifts_delivery")

# Add constraint to ensure the number of trips made by the new company does not exceed the maximum
model.addConstr(TripsNew <= MaxTripsNew, name="max_trips_constraint")

# Add constraint to ensure the old company makes at least the minimum percentage of all trips
model.addConstr(TripsOld >= (MinPercentOld / (1 - MinPercentOld)) * TripsNew, name="min_percent_old_trips")

# Set objective
model.setObjective(DieselNew * TripsNew + DieselOld * TripsOld, gp.GRB.MINIMIZE)

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
