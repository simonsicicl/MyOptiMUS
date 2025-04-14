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
NumberOfBusTrips = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfBusTrips")
NumberOfCarTrips = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfCarTrips")

# Since the variable NumberOfBusTrips has already been defined as an INTEGER and is non-negative by default,
# no additional constraint is necessary to ensure it is non-negative.
# Gurobi integer variables are non-negative by default unless specified otherwise.

# Constraint to ensure the number of car trips is non-negative
model.addConstr(NumberOfCarTrips >= 0, name="non_negative_car_trips")

# Constraint: Total number of bus trips cannot exceed the maximum allowed bus trips
model.addConstr(NumberOfBusTrips <= MaxBusTrips, name="max_bus_trips_constraint")

# At least MinCarTripProportion proportion of the trips must be by car
model.addConstr(NumberOfCarTrips >= MinCarTripProportion * (NumberOfCarTrips + NumberOfBusTrips), name="MinCarTripProportionConstraint")

# Add constraint to ensure total number of monkeys transported is at least TotalMonkeys
model.addConstr(BusCapacity * NumberOfBusTrips + CarCapacity * NumberOfCarTrips >= TotalMonkeys, name="total_monkeys_transport")

# Ensure that the total number of monkeys transported is at least equal to the total number of monkeys
model.addConstr((NumberOfBusTrips * BusCapacity) + (NumberOfCarTrips * CarCapacity) >= TotalMonkeys, "min_monkeys_transported")

# Add constraint to limit the number of bus trips
model.addConstr(NumberOfBusTrips <= MaxBusTrips, name="limit_bus_trips")

# Ensure the minimum proportion of car trips
model.addConstr(NumberOfCarTrips >= MinCarTripProportion * (NumberOfCarTrips + NumberOfBusTrips), name="min_car_trip_proportion_constraint")

# Set objective
model.setObjective(NumberOfBusTrips * BusDuration + NumberOfCarTrips * CarDuration, gp.GRB.MINIMIZE)

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
