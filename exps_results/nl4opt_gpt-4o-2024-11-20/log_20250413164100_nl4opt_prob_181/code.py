import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_181/data.json", "r") as f:
    data = json.load(f)

SubmarineCapacity = data["SubmarineCapacity"] # scalar parameter
SubmarineFuel = data["SubmarineFuel"] # scalar parameter
BoatCapacity = data["BoatCapacity"] # scalar parameter
BoatFuel = data["BoatFuel"] # scalar parameter
MaxSubmarineTrips = data["MaxSubmarineTrips"] # scalar parameter
MinBoatTripProportion = data["MinBoatTripProportion"] # scalar parameter
MinMail = data["MinMail"] # scalar parameter
NumberOfSubmarineTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfSubmarineTrips")
NumberOfBoatTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfBoatTrips")
TotalTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalTrips")

# No code needed, as non-negativity is defined inherently for variables in gurobipy unless explicitly set otherwise.

# As the non-negativity constraint is inherent to the variable's domain (continuous variables in Gurobi are non-negative by default unless explicitly bounded to be negative), no additional constraint code is needed.

# Add constraint to limit the number of submarine trips
model.addConstr(NumberOfSubmarineTrips <= MaxSubmarineTrips, name="submarine_trip_limit")

# Add constraint to ensure at least MinBoatTripProportion of the trips are by boat
model.addConstr(
    NumberOfBoatTrips >= (MinBoatTripProportion * NumberOfSubmarineTrips) / (1 - MinBoatTripProportion),
    name="min_boat_trip_proportion"
)

# Add minimum mail transportation constraint
model.addConstr(
    SubmarineCapacity * NumberOfSubmarineTrips + BoatCapacity * NumberOfBoatTrips >= MinMail,
    name="min_mail_transportation"
)

# Add constraint for minimum mail requirement
model.addConstr(
    SubmarineCapacity * NumberOfSubmarineTrips + BoatCapacity * NumberOfBoatTrips >= MinMail,
    name="min_mail_requirement"
)

# Add constraint to limit the number of submarine trips
model.addConstr(NumberOfSubmarineTrips <= MaxSubmarineTrips, name="submarine_trip_limit")

# Add constraint to ensure a minimum proportion of trips must be made using boats
model.addConstr(
    NumberOfBoatTrips >= MinBoatTripProportion * (NumberOfSubmarineTrips + NumberOfBoatTrips),
    name="min_boat_trip_proportion"
)

# Add constraint to define TotalTrips as the sum of NumberOfSubmarineTrips and NumberOfBoatTrips
model.addConstr(TotalTrips == NumberOfSubmarineTrips + NumberOfBoatTrips, name="total_trips_definition")

# Add non-negativity constraints for the number of trips
model.addConstr(NumberOfSubmarineTrips >= 0, name="non_negativity_submarine_trips")
model.addConstr(NumberOfBoatTrips >= 0, name="non_negativity_boat_trips")

# Set objective
model.setObjective(SubmarineFuel * NumberOfSubmarineTrips + BoatFuel * NumberOfBoatTrips, gp.GRB.MINIMIZE)

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
