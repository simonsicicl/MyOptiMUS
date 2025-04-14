import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_245/data.json", "r") as f:
    data = json.load(f)

LargeShipCapacity = data["LargeShipCapacity"] # scalar parameter
LargeShipPollution = data["LargeShipPollution"] # scalar parameter
SmallShipCapacity = data["SmallShipCapacity"] # scalar parameter
SmallShipPollution = data["SmallShipPollution"] # scalar parameter
MaxLargeShipTrips = data["MaxLargeShipTrips"] # scalar parameter
MinSmallShipTripPercent = data["MinSmallShipTripPercent"] # scalar parameter
MinCustomers = data["MinCustomers"] # scalar parameter
NumLargeShipTrips = model.addVar(vtype=gp.GRB.INTEGER, name="NumLargeShipTrips")
NumSmallShipTrips = model.addVar(vtype=gp.GRB.INTEGER, name="NumSmallShipTrips")

# The number of large cruise ship trips is already defined as non-negative by its variable definition
# No additional constraint is needed.

# The number of small cruise ship trips must be non-negative
model.addConstr(NumSmallShipTrips >= 0, name="non_negativity_small_ship_trips")

# Constraint: Number of large cruise ship trips must not exceed the maximum allowable trips
model.addConstr(NumLargeShipTrips <= MaxLargeShipTrips, name="max_large_ship_trips")

# At least MinSmallShipTripPercent of total trips must be small cruise ship trips
model.addConstr(NumSmallShipTrips >= MinSmallShipTripPercent * (NumSmallShipTrips + NumLargeShipTrips), "MinSmallShipTripsPercentConstr")

# Add constraint for minimum number of customers transported
model.addConstr(NumLargeShipTrips * LargeShipCapacity + NumSmallShipTrips * SmallShipCapacity >= MinCustomers, name="min_customers_constraint")

# Ensure that large cruise ship trips do not exceed the maximum number
model.addConstr(NumLargeShipTrips <= MaxLargeShipTrips, name="max_large_ship_trips_constraint")

# Ensure that at least a certain percentage of total trips are small cruise ship trips
model.addConstr(NumSmallShipTrips >= MinSmallShipTripPercent * (NumLargeShipTrips + NumSmallShipTrips), name="min_small_ship_trips")

# Ensure minimum number of customers constraint
model.addConstr(NumLargeShipTrips * LargeShipCapacity + NumSmallShipTrips * SmallShipCapacity >= MinCustomers, name="min_customers_transported")

# Set objective
model.setObjective(NumLargeShipTrips * LargeShipPollution + NumSmallShipTrips * SmallShipPollution, gp.GRB.MINIMIZE)

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
