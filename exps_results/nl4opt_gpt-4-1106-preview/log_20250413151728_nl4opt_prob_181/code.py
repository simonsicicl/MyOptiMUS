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
SubmarineTrips = model.addVar(vtype=gp.GRB.INTEGER, name="SubmarineTrips")
BoatTrips = model.addVar(vtype=gp.GRB.INTEGER, name="BoatTrips")

# Since SubmarineTrips has been defined as an integer variable, no explicit constraint is needed to ensure non-negativity
# Gurobi automatically enforces that integer variables are non-negative by default, hence no additional code is necessary

# Since BoatTrips variable should be non-negative, and it is already defined as an integer variable,
# no additional code is needed for this constraint as the non-negativity is inherently enforced by the variable definition in Gurobi.

# Add constraint for the maximum number of submarine trips allowed
model.addConstr(SubmarineTrips <= MaxSubmarineTrips, "max_submarine_trips")

# Ensure at least a certain proportion of the trips are by boat
MinBoatTripProportion = data["MinBoatTripProportion"]  # scalar parameter
model.addConstr(BoatTrips - MinBoatTripProportion * BoatTrips >= MinBoatTripProportion * SubmarineTrips, "min_boat_trip_proportion_constraint")

# Constraint: At least MinMail pieces of mail need to be transported
model.addConstr(SubmarineTrips * SubmarineCapacity + BoatTrips * BoatCapacity >= MinMail, name="min_mail_transportation")

# Add minimum mail transport constraint
model.addConstr(SubmarineCapacity * SubmarineTrips + BoatCapacity * BoatTrips >= MinMail, name="min_mail_transport")

# Add maximum number of submarine trips constraint
model.addConstr(SubmarineTrips <= MaxSubmarineTrips, name="max_submarine_trips")

# Add minimum boat trip proportion constraint
model.addConstr(BoatTrips >= MinBoatTripProportion * (BoatTrips + SubmarineTrips), name="min_boat_trip_proportion")

# Set objective
model.setObjective(SubmarineFuel * SubmarineTrips + BoatFuel * BoatTrips, gp.GRB.MINIMIZE)

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
