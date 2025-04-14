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
HelicopterTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="HelicopterTrips")
TruckTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TruckTrips")

# No additional code needed since the variable "HelicopterTrips" is defined with non-negativity by default through its lower bound of 0 in Gurobi.

# The variable "TruckTrips" is already constrained to be non-negative because it is defined as a continuous variable in Gurobi, which is non-negative by default.

# Add constraint to ensure sufficient transportation of cows
model.addConstr(
    HelicopterTrips * CowsPerHelicopter + TruckTrips * CowsPerTruck >= TotalCows,
    name="cow_transportation_requirement"
)

# Add constraint for total number of truck trips not exceeding the maximum allowed
model.addConstr(TruckTrips <= MaxTruckTrips, name="max_truck_trips")

# The variable "TruckTrips" is already constrained to be non-negative because it is defined as a continuous variable in Gurobi, which is non-negative by default.

# Add constraint to ensure the total number of cows transported meets or exceeds the demand
model.addConstr(
    HelicopterTrips * CowsPerHelicopter + TruckTrips * CowsPerTruck >= TotalCows,
    name="total_cows_transport_demand"
)

# Add constraint to ensure the number of truck trips does not exceed the maximum limit
model.addConstr(TruckTrips <= MaxTruckTrips, name="truck_trip_limit")

# Add constraint to ensure the total number of cows transported equals the total number of cows to transport
model.addConstr(
    CowsPerHelicopter * HelicopterTrips + CowsPerTruck * TruckTrips == TotalCows,
    name="cows_transport_balance"
)

# Add constraint to limit the number of truck trips
model.addConstr(TruckTrips <= MaxTruckTrips, name="truck_trip_limit")

# Set objective
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
