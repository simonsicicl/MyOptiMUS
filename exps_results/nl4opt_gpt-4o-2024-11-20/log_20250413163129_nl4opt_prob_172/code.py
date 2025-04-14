import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_172/data.json", "r") as f:
    data = json.load(f)

BusCapacity = data["BusCapacity"] # scalar parameter
BusTripTime = data["BusTripTime"] # scalar parameter
MaxBusTrips = data["MaxBusTrips"] # scalar parameter
MinimumCarTripPercentage = data["MinimumCarTripPercentage"] # scalar parameter
CarCapacity = data["CarCapacity"] # scalar parameter
CarTripTime = data["CarTripTime"] # scalar parameter
TotalChicken = data["TotalChicken"] # scalar parameter
NumberOfBusTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfBusTrips")
NumberOfCarTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfCarTrips")
TotalTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalTrips")
TotalTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalTrips")

# The variable "NumberOfBusTrips" is non-negative due to its default lower bound (0) in Gurobi's variable definition.

# Ensure the number of car trips is non-negative
model.addConstr(NumberOfCarTrips >= 0, name="non_negative_car_trips")

# Add the constraint to ensure the number of bus trips does not exceed the maximum allowed
model.addConstr(NumberOfBusTrips <= MaxBusTrips, name="max_bus_trips")

# Add constraint to ensure at least MinimumCarTripPercentage of trips are by car
model.addConstr(NumberOfCarTrips >= MinimumCarTripPercentage * TotalTrips, name="MinimumCarTripPercentageConstraint")

# Add chicken transportation constraint
model.addConstr(
    NumberOfBusTrips * BusCapacity + NumberOfCarTrips * CarCapacity >= TotalChicken,
    name="chicken_transportation_constraint"
)

# Add constraint: TotalTrips is the sum of car and bus trips
model.addConstr(TotalTrips == NumberOfCarTrips + NumberOfBusTrips, name="total_trips_constraint")

# Add constraint to ensure the total chickens transported matches the total demand
model.addConstr(BusCapacity * NumberOfBusTrips + CarCapacity * NumberOfCarTrips == TotalChicken, name="chicken_transport_demand")

# Add constraint to enforce that the number of bus trips does not exceed the maximum allowed
model.addConstr(NumberOfBusTrips <= MaxBusTrips, name="bus_trip_limit")

# Add minimum car trip percentage constraint
model.addConstr(NumberOfCarTrips >= MinimumCarTripPercentage * (NumberOfCarTrips + NumberOfBusTrips), name="min_car_trip_percentage")

# Set objective
model.setObjective(BusTripTime * NumberOfBusTrips + CarTripTime * NumberOfCarTrips, gp.GRB.MINIMIZE)

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
