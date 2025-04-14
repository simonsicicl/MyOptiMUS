import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_191/data.json", "r") as f:
    data = json.load(f)

PackageTruck = data["PackageTruck"] # scalar parameter
PackageCar = data["PackageCar"] # scalar parameter
GasTruck = data["GasTruck"] # scalar parameter
GasCar = data["GasCar"] # scalar parameter
MaxTruckTrips = data["MaxTruckTrips"] # scalar parameter
MinCarTripProp = data["MinCarTripProp"] # scalar parameter
MinPackages = data["MinPackages"] # scalar parameter
TruckTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TruckTrips")
CarTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CarTrips")

# No constraint code needed: Gurobi variables by default enforce non-negativity for continuous variables unless specified otherwise.

# No code is needed: Gurobi variables by default have non-negativity constraints unless explicitly set otherwise.

# Add constraint to ensure that the number of truck trips doesn't exceed the maximum allowed trips
model.addConstr(TruckTrips <= MaxTruckTrips, name="truck_trip_limit")

# Add constraint to ensure at least MinCarTripProp of all trips are made by cars
model.addConstr((1 - MinCarTripProp) * CarTrips - MinCarTripProp * TruckTrips >= 0, name="min_car_trip_proportion")

# Add constraint to ensure at least MinPackages packages are transported
model.addConstr(TruckTrips * PackageTruck + CarTrips * PackageCar >= MinPackages, name="min_packages_transport")

# Add constraint to ensure total trips are greater than or equal to 1
model.addConstr(TruckTrips + CarTrips >= 1, name="total_trips_nonzero")

# No code needed: The non-negativity of TruckTrips is implicitly enforced by Gurobi since it is added as a continuous variable (vtype=gp.GRB.CONTINUOUS), which defaults to non-negative unless explicitly specified otherwise.

# CarTrips is already non-negative because it is defined as a continuous variable by default in Gurobi.

# Add constraint to ensure the total packages transported meets the minimum requirement
model.addConstr((PackageTruck * TruckTrips) + (PackageCar * CarTrips) >= MinPackages, name="min_packages_constraint")

# Add constraint to restrict the number of truck trips
model.addConstr(TruckTrips <= MaxTruckTrips, name="max_truck_trips")

# Add the constraint ensuring the proportion of trips made by cars meets the minimum required proportion
model.addConstr((1 - MinCarTripProp) * CarTrips >= MinCarTripProp * TruckTrips, name="min_car_trip_proportion")

# Set objective
model.setObjective((GasTruck * TruckTrips) + (GasCar * CarTrips), gp.GRB.MINIMIZE)

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
