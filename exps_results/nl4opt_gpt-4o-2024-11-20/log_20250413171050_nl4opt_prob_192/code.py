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
PatientsTransportedByHelicopter = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PatientsTransportedByHelicopter")
PatientsTransportedByBus = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PatientsTransportedByBus")
HelicopterTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="HelicopterTrips")
BusTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="BusTrips")

# Constraint not needed: non-negativity is automatically enforced by the variable type (CONTINUOUS)

# The non-negativity of PatientsTransportedByBus is inherently ensured as it is defined as a continuous variable (default lower bound is 0).

# Ensure consistency with the percentage of helicopter trips
model.addConstr(
    HelicopterTrips >= MinHelicopterTripsPercentage * (HelicopterTrips + BusTrips),
    name="min_helicopter_trips_percentage"
)

# Add constraints to ensure BusTrips is non-negative and does not exceed MaxBusTrips
model.addConstr(BusTrips >= 0, name="min_bus_trips")
model.addConstr(BusTrips <= MaxBusTrips, name="max_bus_trips")

model.addConstr(HelicopterTrips == PatientsTransportedByHelicopter / HelicopterCapacity, name="helicopter_trips_definition")

# Add constraint to relate BusTrips and PatientsTransportedByBus based on BusCapacity
model.addConstr(BusTrips == PatientsTransportedByBus / BusCapacity, name="bus_trips_calculation")

# Add constraint ensuring transported patients equal trips times capacity
model.addConstr(PatientsTransportedByHelicopter == HelicopterTrips * HelicopterCapacity, name="helicopter_transport_constraint")

# Add constraint to link patients transported by bus, bus trips, and bus capacity
model.addConstr(PatientsTransportedByBus == BusTrips * BusCapacity, name="patients_transportation_constraint")

# Add minimum patient transportation constraint
model.addConstr(PatientsTransportedByHelicopter + PatientsTransportedByBus >= MinPatients, name="min_patient_transport")

# Add minimum helicopter trips proportion constraint
model.addConstr(HelicopterTrips >= MinHelicopterTripsPercentage * (HelicopterTrips + BusTrips), name="min_helicopter_trips_percentage")

# Add constraint to enforce that the number of bus trips does not exceed the maximum allowed
model.addConstr(BusTrips <= MaxBusTrips, name="bus_trip_limit")

# Set objective
model.setObjective(HelicopterTrips * HelicopterTripTime + BusTrips * BusTripTime, gp.GRB.MINIMIZE)

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
