import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_151/data.json", "r") as f:
    data = json.load(f)

ShipCapacity = data["ShipCapacity"] # scalar parameter
ShipFuel = data["ShipFuel"] # scalar parameter
PlaneCapacity = data["PlaneCapacity"] # scalar parameter
PlaneFuel = data["PlaneFuel"] # scalar parameter
MinContainers = data["MinContainers"] # scalar parameter
MaxPlaneTrips = data["MaxPlaneTrips"] # scalar parameter
MinShipTripPercentage = data["MinShipTripPercentage"] # scalar parameter
NumberOfShipTrips = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfShipTrips")
NumberOfPlaneTrips = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfPlaneTrips")

# Constraint to ensure the number of ship trips is non-negative
model.addConstr(NumberOfShipTrips >= 0, name="non_negative_ship_trips")

# Since NumberOfPlaneTrips is already defined as an integer variable, we just need to add a constraint to ensure it is non-negative
model.addConstr(NumberOfPlaneTrips >= 0, name="non_negative_trips")

# Add constraint for the minimum number of containers transported by ship and plane combined
model.addConstr(NumberOfShipTrips * ShipCapacity + NumberOfPlaneTrips * PlaneCapacity >= MinContainers, name="min_containers_ship_plane")

# At most MaxPlaneTrips plane trips can be made
model.addConstr(NumberOfPlaneTrips <= MaxPlaneTrips, name="max_plane_trips_constraint")

# Ensure at least MinShipTripPercentage% of trips are by ship
NumberOfTotalTrips = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfTotalTrips")

model.addConstr(NumberOfTotalTrips == NumberOfShipTrips + NumberOfPlaneTrips, name="calc_NumberOfTotalTrips")
model.addConstr(NumberOfShipTrips >= MinShipTripPercentage * NumberOfTotalTrips, name="min_ship_trip_percentage")

# Ensure at least the minimum number of containers are transported
model.addConstr(
    NumberOfShipTrips * ShipCapacity + NumberOfPlaneTrips * PlaneCapacity >= MinContainers,
    name="min_containers_requirement"
)

# Add constraint to ensure the number of plane trips does not exceed the maximum allowed
model.addConstr(NumberOfPlaneTrips <= MaxPlaneTrips, name="max_plane_trips")

# Ensure at least the minimum percentage of trips are made by ships
NumberOfShipTrips = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfShipTrips")
NumberOfPlaneTrips = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfPlaneTrips")
MinShipTripPercentage = data["MinShipTripPercentage"]  # scalar parameter

# Add the constraint: NumberOfShipTrips >= (MinShipTripPercentage * (NumberOfShipTrips + NumberOfPlaneTrips)) / (1 - MinShipTripPercentage)
model.addConstr(NumberOfShipTrips >= (MinShipTripPercentage * (NumberOfShipTrips + NumberOfPlaneTrips)) / (1 - MinShipTripPercentage), name="min_ship_trips")

# Define the objective function
model.setObjective(NumberOfShipTrips * ShipFuel + NumberOfPlaneTrips * PlaneFuel, gp.GRB.MINIMIZE)

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
