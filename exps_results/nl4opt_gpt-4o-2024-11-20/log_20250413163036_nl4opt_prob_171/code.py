import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_171/data.json", "r") as f:
    data = json.load(f)

RegularCapacity = data["RegularCapacity"] # scalar parameter
RegularFuel = data["RegularFuel"] # scalar parameter
SpeedCapacity = data["SpeedCapacity"] # scalar parameter
SpeedFuel = data["SpeedFuel"] # scalar parameter
MaxRegularTrips = data["MaxRegularTrips"] # scalar parameter
MinSpeedPercentage = data["MinSpeedPercentage"] # scalar parameter
TotalMail = data["TotalMail"] # scalar parameter
RegularTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="RegularTrips")
SpeedTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SpeedTrips")
TotalTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalTrips")

# The non-negativity constraint for RegularTrips is implicitly satisfied by Gurobi's default lower bound of zero for continuous variables.

# The non-negativity constraint for SpeedTrips is inherently satisfied as it is defined as a continuous variable in Gurobi, which is non-negative by default.

# Add the constraint that the number of regular trips cannot exceed the maximum allowed
model.addConstr(RegularTrips <= MaxRegularTrips, name="regular_trips_limit")

# Add constraint for minimum speed boats percentage
model.addConstr((1 - MinSpeedPercentage) * SpeedTrips >= MinSpeedPercentage * RegularTrips, name="min_speed_boats_percentage")

# Add constraint to ensure total mail delivered is at least TotalMail
model.addConstr(RegularTrips * RegularCapacity + SpeedTrips * SpeedCapacity >= TotalMail, name="mail_delivery_constraint")

# Add constraint to ensure RegularTrips does not exceed MaxRegularTrips
model.addConstr(RegularTrips <= MaxRegularTrips, name="max_regular_trips")

# Add constraint ensuring at least a minimum percentage of trips must be made by speed boats
model.addConstr(SpeedTrips >= MinSpeedPercentage * (RegularTrips + SpeedTrips), name="speed_trip_minimum_percentage")

# Add constraint to ensure total trips is the sum of regular and speed boat trips
model.addConstr(TotalTrips == RegularTrips + SpeedTrips, name="total_trips_constraint")

# Add constraint ensuring total trips is the sum of regular boat trips and speed boat trips
model.addConstr(TotalTrips == RegularTrips + SpeedTrips, name="total_trips_constraint")

# Add constraint to relate TotalTrips, RegularTrips, and SpeedTrips
model.addConstr(TotalTrips == RegularTrips + SpeedTrips, name="trips_sum_constraint")

# Add constraint to ensure total mail demand is met by the combined capacity of regular and speed trips
model.addConstr(RegularTrips * RegularCapacity + SpeedTrips * SpeedCapacity >= TotalMail, name="mail_demand_constraint")

# Add constraint to ensure the total number of trips by regular boats does not exceed the maximum allowed
model.addConstr(RegularTrips <= MaxRegularTrips, name="max_regular_trips_constraint")

# Add constraint to ensure a minimum percentage of trips are completed using speed boats
model.addConstr(SpeedTrips >= MinSpeedPercentage * TotalTrips, name="min_speed_boat_trips")

# Set objective
model.setObjective(RegularFuel * RegularTrips + SpeedFuel * SpeedTrips, gp.GRB.MINIMIZE)

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
