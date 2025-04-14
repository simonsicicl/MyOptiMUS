import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_262/data.json", "r") as f:
    data = json.load(f)

MinLocals = data["MinLocals"] # scalar parameter
PeoplePerKayak = data["PeoplePerKayak"] # scalar parameter
PeoplePerMotorboat = data["PeoplePerMotorboat"] # scalar parameter
TimePerKayak = data["TimePerKayak"] # scalar parameter
TimePerMotorboat = data["TimePerMotorboat"] # scalar parameter
MaxMotorboatTrips = data["MaxMotorboatTrips"] # scalar parameter
MinPercentKayakTrips = data["MinPercentKayakTrips"] # scalar parameter
KayakTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="KayakTrips")
MotorboatTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MotorboatTrips")
TotalPeopleMovedByMotorboats = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalPeopleMovedByMotorboats")
TotalTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalTrips")

# Add constraint to ensure at least MinLocals locals are transported across the lake
model.addConstr(
    PeoplePerKayak * KayakTrips + PeoplePerMotorboat * MotorboatTrips >= MinLocals,
    name="min_locals_transport"
)

# Add transportation constraints
model.addConstr(KayakTrips * PeoplePerKayak + MotorboatTrips * PeoplePerMotorboat >= MinLocals, name="min_locals_transport")
model.addConstr(MotorboatTrips <= MaxMotorboatTrips, name="motorboat_trip_limit")

# Add motorboat transportation capacity constraint
model.addConstr(TotalPeopleMovedByMotorboats <= MotorboatTrips * PeoplePerMotorboat, name="motorboat_transport_capacity")

# Add constraint to ensure motorboat trips do not exceed maximum allowable limit
model.addConstr(MotorboatTrips <= MaxMotorboatTrips, name="max_motorboat_trips")

# Add constraint to ensure at least MinPercentKayakTrips percent of total trips are by kayak
model.addConstr((1 - MinPercentKayakTrips) * KayakTrips >= MinPercentKayakTrips * MotorboatTrips, name="kayak_trip_minimum")

# Add constraint ensuring percentage of kayak trips meets minimum required percentage
model.addConstr(
    KayakTrips >= MinPercentKayakTrips * (KayakTrips + MotorboatTrips),
    name="min_percentage_kayak_trips"
)

# Add a constraint to calculate the total number of people transported by motorboats
model.addConstr(TotalPeopleMovedByMotorboats == MotorboatTrips * PeoplePerMotorboat, name="total_people_moved_by_motorboats")

# Add constraint to ensure the total number of people transported meets the minimum required number of locals
model.addConstr(
    PeoplePerKayak * KayakTrips + PeoplePerMotorboat * MotorboatTrips >= MinLocals,
    name="min_locals_constraint"
)

# Add constraint to ensure the total number of motorboat trips does not exceed the maximum allowed
model.addConstr(MotorboatTrips <= MaxMotorboatTrips, name="motorboat_trip_limit")

# Add constraint to ensure minimum percentage of kayak trips
model.addConstr(KayakTrips >= MinPercentKayakTrips * TotalTrips, name="min_percentage_kayak_trips")

# Add constraint ensuring total number of trips equals the sum of kayak and motorboat trips
model.addConstr(TotalTrips == KayakTrips + MotorboatTrips, name="total_trips_constraint")

# Set objective
model.setObjective(TimePerKayak * KayakTrips + TimePerMotorboat * MotorboatTrips, gp.GRB.MINIMIZE)

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
