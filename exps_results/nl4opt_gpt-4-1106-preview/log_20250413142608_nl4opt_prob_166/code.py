import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_166/data.json", "r") as f:
    data = json.load(f)

LargePlaneCapacity = data["LargePlaneCapacity"] # scalar parameter
SmallPlaneCapacity = data["SmallPlaneCapacity"] # scalar parameter
MinimumCarsDelivered = data["MinimumCarsDelivered"] # scalar parameter
PollutionRatio = data["PollutionRatio"] # scalar parameter
NumLargePlanes = model.addVar(vtype=gp.GRB.INTEGER, name="NumLargePlanes")
NumSmallPlanes = model.addVar(vtype=gp.GRB.INTEGER, name="NumSmallPlanes")

# Add constraint for the number of large planes used to be less than PollutionRatio times the number of small planes
model.addConstr(NumLargePlanes <= PollutionRatio * NumSmallPlanes, "large_to_small_plane_ratio")

# Constraint to ensure that at least the minimum number of cars is delivered
model.addConstr(NumLargePlanes * LargePlaneCapacity + NumSmallPlanes * SmallPlaneCapacity >= MinimumCarsDelivered, "min_cars_delivery")

# Constraint: The number of large planes used must be non-negative
model.addConstr(NumLargePlanes >= 0, "c_NumLargePlanes_non_negative")

# Constraint to ensure the number of small planes used is non-negative
model.addConstr(NumSmallPlanes >= 0, "num_small_planes_non_negative")

# Ensure that enough planes are used to meet the shipping demand for the minimum number of cars to be delivered
model.addConstr(NumLargePlanes * LargePlaneCapacity + NumSmallPlanes * SmallPlaneCapacity >= MinimumCarsDelivered, name="meet_shipping_demand")

# Set objective
model.setObjective(NumLargePlanes + NumSmallPlanes, gp.GRB.MINIMIZE)

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
