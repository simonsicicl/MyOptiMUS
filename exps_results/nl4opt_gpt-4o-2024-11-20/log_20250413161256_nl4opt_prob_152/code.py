import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_152/data.json", "r") as f:
    data = json.load(f)

DucksPerBoat = data["DucksPerBoat"] # scalar parameter
DucksPerCanoe = data["DucksPerCanoe"] # scalar parameter
TimePerBoat = data["TimePerBoat"] # scalar parameter
TimePerCanoe = data["TimePerCanoe"] # scalar parameter
MaxBoatTrips = data["MaxBoatTrips"] # scalar parameter
MinCanoeTripsPercentage = data["MinCanoeTripsPercentage"] # scalar parameter
MinDucks = data["MinDucks"] # scalar parameter
NumBoatTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumBoatTrips")
NumCanoeTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumCanoeTrips")
TotalDucksByBoat = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalDucksByBoat")
TotalDucksByCanoe = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalDucksByCanoe")
TotalTime = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalTime")

# The non-negativity constraint for NumBoatTrips is already enforced by the variable's default lower bound of 0. No additional code is required.

# Add constraint to ensure the number of canoe trips is non-negative
model.addConstr(NumCanoeTrips >= 0, name="non_negative_canoe_trips")

# Add constraint ensuring total ducks transported by boats equals ducks per boat multiplied by total boat trips
model.addConstr(TotalDucksByBoat == DucksPerBoat * NumBoatTrips, name="ducks_transportation_consistency")

# Add constraint to ensure the total number of ducks transported by canoes does not exceed the product of canoe trips and ducks per canoe trip
model.addConstr(TotalDucksByCanoe <= NumCanoeTrips * DucksPerCanoe, name="ducks_transport_limit")

# Add constraint to limit the total number of boat trips to a maximum value
model.addConstr(NumBoatTrips <= MaxBoatTrips, name="max_boat_trips")

# Add a constraint to ensure at least the minimum required percentage of trips are by canoe
model.addConstr(
    NumCanoeTrips >= (MinCanoeTripsPercentage / (1 - MinCanoeTripsPercentage)) * NumBoatTrips, 
    name="min_canoe_percentage"
)

# Add constraint to ensure at least MinDucks are transported to shore
model.addConstr(TotalDucksByBoat + TotalDucksByCanoe >= MinDucks, name="min_duck_transport")

# Add constraint that total number of ducks transported by canoes equals DucksPerCanoe multiplied by NumCanoeTrips
model.addConstr(TotalDucksByCanoe == DucksPerCanoe * NumCanoeTrips, name="ducks_transport_constraint")

# Add constraint to ensure all ducks are transported
model.addConstr(TotalDucksByBoat + TotalDucksByCanoe >= MinDucks, name="ensure_ducks_transport")

# Add constraint to define total ducks transported by boats
model.addConstr(TotalDucksByBoat == DucksPerBoat * NumBoatTrips, name="TotalDucksByBoat_constraint")

# Add constraint for total ducks transported by canoes
model.addConstr(TotalDucksByCanoe == DucksPerCanoe * NumCanoeTrips, name="ducks_transport_constraint")

# Add constraint to limit the total number of boat trips
model.addConstr(NumBoatTrips <= MaxBoatTrips, name="limit_boat_trips")

# Add constraint to ensure canoe trips meet the minimum percentage of total trips
model.addConstr(NumCanoeTrips >= MinCanoeTripsPercentage * (NumBoatTrips + NumCanoeTrips), name="canoe_min_percentage")

# Add constraint linking TotalTime to the weighted sum of boat and canoe times
model.addConstr(TotalTime == TimePerBoat * NumBoatTrips + TimePerCanoe * NumCanoeTrips, name="link_totaltime_weighted_sum")

# Set objective
model.setObjective(TotalTime, gp.GRB.MINIMIZE)

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
