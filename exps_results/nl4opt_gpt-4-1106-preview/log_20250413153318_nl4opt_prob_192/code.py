import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_192/data.json", "r") as f:
    data = json.load(f)

HelicopterCapacity = data["HelicopterCapacity"] # scalar parameter
HelicopterTripTime = data["HelicopterTripTime"] # scalar parameter
BusCapacity = data["BusCapacity"] # scalar parameter
BusTripTime = data["BusTripTime"] # scalar parameter
MinPatients = data["MinPatients"] # scalar parameter
MinHelicopterTripsPercentage = data["MinHelicopterTripsPercentage"] # scalar parameter
MaxBusTrips = data["MaxBusTrips"] # scalar parameter
PatientsHelicopterTrips = model.addVar(vtype=gp.GRB.INTEGER, name="PatientsHelicopterTrips")
PatientsBusTrips = model.addVar(vtype=gp.GRB.INTEGER, name="PatientsBusTrips")

# The number of helicopter trips must be non-negative, so no constraint is needed as
# Gurobi variables are non-negative by default unless otherwise specified.
# The code to define this variable as an integer non-negative variable has already been provided.

# Since the variable PatientsBusTrips is already defined as an integer, we only need to set the non-negativity constraint
model.addConstr(PatientsBusTrips >= 0, name="non_negativity_patients_bustrips")

# At least MinHelicopterTripsPercentage of the total number of trips must be by helicopter
model.addConstr(PatientsHelicopterTrips >= MinHelicopterTripsPercentage * (PatientsHelicopterTrips + PatientsBusTrips), "min_helicopter_trips_constraint")

# Add constraint to ensure the number of bus trips is non-negative and limited to maximum allowed trips
model.addConstr(PatientsBusTrips >= 0, name="min_bus_trips")
model.addConstr(PatientsBusTrips <= MaxBusTrips, name="max_bus_trips")

# Ensure that the minimum number of patients is transported
model.addConstr(PatientsHelicopterTrips * HelicopterCapacity + PatientsBusTrips * BusCapacity >= MinPatients, "min_patients_transported")

# Ensure that at least the minimum percentage of trips are made by the helicopters
total_trips = gp.LinExpr(PatientsHelicopterTrips + PatientsBusTrips)
model.addConstr(PatientsHelicopterTrips >= MinHelicopterTripsPercentage * total_trips, "min_helicopter_trips")

# Ensure that the maximum number of bus trips is not exceeded
model.addConstr(PatientsBusTrips <= MaxBusTrips, name="max_bus_trips")

# Set objective
model.setObjective(PatientsHelicopterTrips * HelicopterTripTime + PatientsBusTrips * BusTripTime, gp.GRB.MINIMIZE)

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
