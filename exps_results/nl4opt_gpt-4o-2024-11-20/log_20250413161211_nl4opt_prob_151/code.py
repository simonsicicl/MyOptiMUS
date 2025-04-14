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
ShipTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ShipTrips")
PlaneTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PlaneTrips")
TotalTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalTrips")

# No constraint code needed: Gurobi variables by default enforce non-negativity for continuous variables unless specified otherwise.

# No code needed as the Gurobi model automatically ensures the non-negativity of continuous variables by default unless defined with lower bounds less than zero.

# Add constraint to ensure the total number of containers transported meets or exceeds MinContainers
model.addConstr(ShipCapacity * ShipTrips + PlaneCapacity * PlaneTrips >= MinContainers, name="min_containers_requirement")

# Add constraint to limit the number of plane trips
model.addConstr(PlaneTrips <= MaxPlaneTrips, name="max_plane_trips")

# Add constraint for minimum percentage of trips made by ship
model.addConstr(
    ShipTrips * (1 - MinShipTripPercentage) >= MinShipTripPercentage * PlaneTrips,
    name="min_ship_trip_percentage"
)

# Add constraint to ensure the total number of containers transported meets or exceeds the minimum required
model.addConstr(
    (ShipCapacity * ShipTrips) + (PlaneCapacity * PlaneTrips) >= MinContainers, 
    name="min_containers_transport"
)

# Add constraint for the maximum number of plane trips
model.addConstr(PlaneTrips <= MaxPlaneTrips, name="max_plane_trips")

# Add constraint to ensure at least a specified percentage of total trips are made by ships
model.addConstr(ShipTrips >= MinShipTripPercentage * TotalTrips, name="min_ship_trip_percentage")

# Add constraint to ensure the total trips is the sum of ship trips and plane trips
model.addConstr(TotalTrips == ShipTrips + PlaneTrips, name="total_trips_constraint")

# Set objective
model.setObjective((ShipFuel * ShipTrips) + (PlaneFuel * PlaneTrips), gp.GRB.MINIMIZE)

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
