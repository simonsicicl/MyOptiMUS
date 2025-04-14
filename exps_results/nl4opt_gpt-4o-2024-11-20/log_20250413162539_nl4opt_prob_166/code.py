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
NumLargePlanes = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumLargePlanes")
NumSmallPlanes = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumSmallPlanes")

# Add constraint to ensure the number of large planes is less than or equal to PollutionRatio times the number of small planes
model.addConstr(NumLargePlanes <= PollutionRatio * NumSmallPlanes, name="large_small_planes_ratio")

# Add constraint to ensure at least MinimumCarsDelivered cars are delivered
model.addConstr(NumLargePlanes * LargePlaneCapacity + NumSmallPlanes * SmallPlaneCapacity >= MinimumCarsDelivered, name="minimum_cars_delivered")

# The variable NumLargePlanes is already defined as non-negative due to its default properties (continuous variables in Gurobi are non-negative by default), so no additional constraint is needed.

# The variable NumSmallPlanes is already defined as non-negative due to its default properties (continuous variables in Gurobi are non-negative unless stated otherwise); no additional constraint is needed.

# Add constraint to ensure the total capacity of planes meets or exceeds the minimum number of cars to be delivered
model.addConstr(
    LargePlaneCapacity * NumLargePlanes + SmallPlaneCapacity * NumSmallPlanes >= MinimumCarsDelivered,
    name="plane_capacity_constraint"
)

# Add pollution factor constraint for large planes
model.addConstr(NumLargePlanes - PollutionRatio * (NumLargePlanes + NumSmallPlanes) <= 0, name="pollution_factor_large_planes")

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
