import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_182/data.json", "r") as f:
    data = json.load(f)

FishPerHelicopter = data["FishPerHelicopter"] # scalar parameter
TimeHelicopter = data["TimeHelicopter"] # scalar parameter
FishPerCar = data["FishPerCar"] # scalar parameter
TimeCar = data["TimeCar"] # scalar parameter
MaxHelicopterTrips = data["MaxHelicopterTrips"] # scalar parameter
CarTripPercentage = data["CarTripPercentage"] # scalar parameter
MinFishNeeded = data["MinFishNeeded"] # scalar parameter
HelicopterTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="HelicopterTrips")
CarTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CarTrips")

# No additional code needed since the variable HellicopterTrips is already non-negative due to its default lower bound (0) in Gurobi.

# No additional code is necessary because the non-negativity constraint is automatically enforced
# by defining CarTrips with the default lower bound of 0 in Gurobi.

# Add constraint to ensure at least MinFishNeeded fish are transported
model.addConstr(
    HelicopterTrips * FishPerHelicopter + CarTrips * FishPerCar >= MinFishNeeded,
    name="min_fish_transport"
)

# Add constraint to limit the number of helicopter trips
model.addConstr(HelicopterTrips <= MaxHelicopterTrips, name="helicopter_trips_limit")

# Add constraint for minimum car trip percentage
model.addConstr((1 - CarTripPercentage) * CarTrips >= CarTripPercentage * HelicopterTrips, name="min_car_trip_percentage")

# Add constraint to ensure minimum number of fish are transported
model.addConstr(HelicopterTrips * FishPerHelicopter + CarTrips * FishPerCar >= MinFishNeeded, name="min_fish_transport")

# Add constraint to limit the number of helicopter trips
model.addConstr(HelicopterTrips <= MaxHelicopterTrips, name="helicopter_trip_limit")

# Add constraint to ensure at least the specified percentage of trips are by car
model.addConstr(CarTrips * (1 - CarTripPercentage) >= CarTripPercentage * HelicopterTrips, name="car_trip_percentage")

# Set objective
model.setObjective(HelicopterTrips * TimeHelicopter + CarTrips * TimeCar, gp.GRB.MINIMIZE)

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
