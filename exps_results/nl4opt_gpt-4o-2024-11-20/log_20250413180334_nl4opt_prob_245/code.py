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
LargeShipTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="LargeShipTrips")
SmallShipTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SmallShipTrips")

# Non-negativity constraint for the number of large cruise ship trips
model.addConstr(LargeShipTrips >= 0, name="non_negative_LargeShipTrips")

# The variable "SmallShipTrips" already has non-negativity enforced internally due to its type being CONTINUOUS in gurobipy.

# Add constraint to ensure the number of large cruise ship trips does not exceed MaxLargeShipTrips
model.addConstr(LargeShipTrips <= MaxLargeShipTrips, name="max_large_ship_trips")

# Add constraint to enforce that at least MinSmallShipTripPercent of total trips are small cruise ship trips
model.addConstr((1 - MinSmallShipTripPercent) * SmallShipTrips >= MinSmallShipTripPercent * LargeShipTrips, 
                name="min_small_ship_trip_constraint")

# Add a constraint to ensure the total number of customers transported is at least the minimum required (MinCustomers)
model.addConstr(
    LargeShipCapacity * LargeShipTrips + SmallShipCapacity * SmallShipTrips >= MinCustomers,
    name="min_customers_constraint"
)

# Add the constraint for the maximum number of large cruise ship trips
model.addConstr(LargeShipTrips <= MaxLargeShipTrips, name="max_large_ship_trips")

# Add the minimum percentage constraint for small cruise ship trips
model.addConstr(SmallShipTrips >= MinSmallShipTripPercent * (LargeShipTrips + SmallShipTrips), name="min_small_ship_trip_percentage")

# Add constraint to ensure total customers transported meets or exceeds target
model.addConstr(
    LargeShipTrips * LargeShipCapacity + SmallShipTrips * SmallShipCapacity >= MinCustomers,
    name="min_customers_constraint"
)

# Set objective
model.setObjective(LargeShipTrips * LargeShipPollution + SmallShipTrips * SmallShipPollution, gp.GRB.MINIMIZE)

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
