import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_163/data.json", "r") as f:
    data = json.load(f)

CowsPerHelicopter = data["CowsPerHelicopter"] # scalar parameter
PollutionPerHelicopter = data["PollutionPerHelicopter"] # scalar parameter
CowsPerTruck = data["CowsPerTruck"] # scalar parameter
PollutionPerTruck = data["PollutionPerTruck"] # scalar parameter
TotalCows = data["TotalCows"] # scalar parameter
MaxTruckTrips = data["MaxTruckTrips"] # scalar parameter
HelicopterTrips = model.addVar(vtype=gp.GRB.INTEGER, name="HelicopterTrips")
TruckTrips = model.addVar(vtype=gp.GRB.INTEGER, name="TruckTrips")

# Since HelicopterTrips is already a non-negative integer variable by virtue of its type, no additional constraint is needed.
# The Gurobi optimizer enforces the non-negativity condition implicitly.

# Constraint: Number of truck trips is non-negative
model.addConstr(TruckTrips >= 0, name="non_negative_truck_trips")

# Ensure total number of cows transported meets or exceeds the TotalCows parameter
model.addConstr(HelicopterTrips * CowsPerHelicopter + TruckTrips * CowsPerTruck >= TotalCows, name="TotalCowsTransported")

# Add constraint for the maximum number of truck trips allowed
model.addConstr(TruckTrips <= MaxTruckTrips, name="max_truck_trips_constraint")

# Ensure that the total number of cows transported meets or exceeds the required amount
model.addConstr(CowsPerHelicopter * HelicopterTrips + CowsPerTruck * TruckTrips >= TotalCows, name="total_cows_transported")

# Ensure that the number of truck trips does not exceed the maximum number allowed
model.addConstr(TruckTrips <= MaxTruckTrips, name="max_truck_trips")

# Define the objective function
model.setObjective(PollutionPerHelicopter * HelicopterTrips + PollutionPerTruck * TruckTrips, gp.GRB.MINIMIZE)

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
