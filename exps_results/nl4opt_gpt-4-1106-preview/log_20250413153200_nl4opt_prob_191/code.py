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
NumberOfTruckTrips = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfTruckTrips")
NumberOfCarTrips = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfCarTrips")

# Since NumberOfTruckTrips is already guaranteed to be non-negative by its variable type,
# no additional constraint is necessary.

# Since NumberOfCarTrips is already an integer variable, no code is needed to enforce non-negativity
# The Gurobi optimizer automatically enforces the non-negative domain for integer variables

# Total number of truck trips should not exceed the maximum allowed truck trips constraint
model.addConstr(NumberOfTruckTrips <= MaxTruckTrips, name="max_truck_trips_constraint")

# Add constraint to ensure at least MinCarTripProp of all trips must be made by cars
model.addConstr((1 - MinCarTripProp) * NumberOfCarTrips >= MinCarTripProp * NumberOfTruckTrips, "MinCarTripsPropConstraint")

# Constraint: At least MinPackages packages must be transported
model.addConstr(NumberOfTruckTrips * PackageTruck + NumberOfCarTrips * PackageCar >= MinPackages, name="min_packages")

# Ensure that the minimum number of packages to be transported is met
model.addConstr(NumberOfTruckTrips * PackageTruck + NumberOfCarTrips * PackageCar >= MinPackages, "min_packages_transported")

# Ensure the number of truck trips does not exceed the maximum
model.addConstr(NumberOfTruckTrips <= MaxTruckTrips, name="max_truck_trips")

# Enforce minimum proportion of trips made by car
model.addConstr(NumberOfCarTrips >= MinCarTripProp * (NumberOfCarTrips + NumberOfTruckTrips), name="min_car_trip_proportion")

# Define the objective function
model.setObjective(NumberOfTruckTrips * GasTruck + NumberOfCarTrips * GasCar, gp.GRB.MINIMIZE)

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
