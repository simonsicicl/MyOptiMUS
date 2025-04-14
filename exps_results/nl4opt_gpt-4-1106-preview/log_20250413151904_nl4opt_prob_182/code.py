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
NumberOfHelicopterTrips = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfHelicopterTrips")
NumberOfCarTrips = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfCarTrips")

# Constraint for non-negative number of helicopter trips
model.addConstr(NumberOfHelicopterTrips >= 0, "non_negativity_helicopter_trips")

# No constraint code needed since the variable NumberOfCarTrips is already defined as non-negative integer by default in Gurobi

# Constraint: Transport at least the minimum number of fish needed
model.addConstr(FishPerHelicopter * NumberOfHelicopterTrips + FishPerCar * NumberOfCarTrips >= MinFishNeeded, name="min_fish_transport")

# Constraint: Number of helicopter trips cannot exceed the maximum allowed
model.addConstr(NumberOfHelicopterTrips <= MaxHelicopterTrips, name="helicopter_trip_constraint")

# Add constraint to ensure that at least CarTripPercentage percent of the total number of trips must be by car
model.addConstr(NumberOfCarTrips >= CarTripPercentage * (NumberOfHelicopterTrips + NumberOfCarTrips), name="car_trip_percentage")

# Ensure the minimum number of fish needed are transported
model.addConstr(FishPerHelicopter * NumberOfHelicopterTrips + FishPerCar * NumberOfCarTrips >= MinFishNeeded, "min_fish_transportation")

# Ensure that the maximum number of helicopter trips is not exceeded
model.addConstr(NumberOfHelicopterTrips <= MaxHelicopterTrips, name="max_helicopter_trips")

# Ensure that the required percentage of trips are by car
total_trips_expr = NumberOfHelicopterTrips + NumberOfCarTrips
required_car_trips = total_trips_expr * CarTripPercentage 
# We use a continuous variable bound by a constraint to represent the ceil of required car trips
model.addConstr(NumberOfCarTrips >= required_car_trips, name="min_car_trips")
# We want to ensure NumberOfCarTrips is greater than or equal to the ceil of required car trips
# Gurobi might have an issue with enforcing ceil directly in constraints, so we model it using an integer constraint trick
epsilon = 1e-5 # A small constant to ensure we take the ceiling
model.addConstr(NumberOfCarTrips >= required_car_trips + (1 - CarTripPercentage) - epsilon, "ceiling_car_trips")

# Define objective function
model.setObjective(TimeHelicopter * NumberOfHelicopterTrips + TimeCar * NumberOfCarTrips, gp.GRB.MINIMIZE)

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
