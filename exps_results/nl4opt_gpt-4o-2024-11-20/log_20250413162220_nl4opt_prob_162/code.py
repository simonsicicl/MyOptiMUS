import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_162/data.json", "r") as f:
    data = json.load(f)

BusCapacity = data["BusCapacity"] # scalar parameter
BusDuration = data["BusDuration"] # scalar parameter
CarCapacity = data["CarCapacity"] # scalar parameter
CarDuration = data["CarDuration"] # scalar parameter
MaxBusTrips = data["MaxBusTrips"] # scalar parameter
MinCarTripProportion = data["MinCarTripProportion"] # scalar parameter
TotalMonkeys = data["TotalMonkeys"] # scalar parameter
NumberOfBusTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfBusTrips")
NumberOfCarTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfCarTrips")
TotalTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalTrips")

# Non-negativity constraint for the number of bus trips
model.addConstr(NumberOfBusTrips >= 0, name="non_negativity_bus_trips")

# No additional code needed since the variable "NumberOfCarTrips" is defined with non-negativity by default through Gurobi's `gp.GRB.CONTINUOUS`.

# Add constraint to ensure the number of bus trips does not exceed the maximum allowed
model.addConstr(NumberOfBusTrips <= MaxBusTrips, name="max_bus_trips")

# Add constraint ensuring minimum proportion of trips are by car
model.addConstr(NumberOfCarTrips >= MinCarTripProportion * TotalTrips, name="min_car_trip_proportion")

# Add constraint to ensure the total monkeys transported by bus and car trips is at least TotalMonkeys
model.addConstr(BusCapacity * NumberOfBusTrips + CarCapacity * NumberOfCarTrips >= TotalMonkeys, name="transport_monkeys_constraint")

# Add transportation capacity constraint
model.addConstr(
    NumberOfBusTrips * BusCapacity + NumberOfCarTrips * CarCapacity >= TotalMonkeys,
    name="transportation_capacity"
)

# Add a constraint to ensure the number of car trips meets the minimum proportion of total trips
model.addConstr(
    NumberOfCarTrips >= MinCarTripProportion * (NumberOfBusTrips + NumberOfCarTrips),
    name="min_car_trip_proportion"
)

# Add constraint for TotalTrips representing the sum of NumberOfBusTrips and NumberOfCarTrips
model.addConstr(TotalTrips == NumberOfBusTrips + NumberOfCarTrips, name="total_trips_constraint")

# Add constraint to ensure all monkeys are transported using buses and cars
model.addConstr(NumberOfBusTrips * BusCapacity + NumberOfCarTrips * CarCapacity >= TotalMonkeys, name="transport_monkeys")

# Add constraint to restrict the number of bus trips within the maximum allowed
model.addConstr(NumberOfBusTrips <= MaxBusTrips, name="max_bus_trips_constraint")

# Add constraint to ensure the number of car trips is at least a given proportion of total trips
model.addConstr(
    NumberOfCarTrips >= MinCarTripProportion * (NumberOfBusTrips + NumberOfCarTrips),
    name="car_trip_proportion"
)

# Add constraint to define TotalTrips as the sum of NumberOfBusTrips and NumberOfCarTrips
model.addConstr(TotalTrips == NumberOfBusTrips + NumberOfCarTrips, name="total_trips_definition")

# Set objective
model.setObjective(
    NumberOfBusTrips * BusDuration + NumberOfCarTrips * CarDuration,
    gp.GRB.MINIMIZE
)

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
