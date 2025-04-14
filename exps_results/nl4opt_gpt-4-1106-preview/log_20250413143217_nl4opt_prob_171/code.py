import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_171/data.json", "r") as f:
    data = json.load(f)

RegularCapacity = data["RegularCapacity"] # scalar parameter
RegularFuel = data["RegularFuel"] # scalar parameter
SpeedCapacity = data["SpeedCapacity"] # scalar parameter
SpeedFuel = data["SpeedFuel"] # scalar parameter
MaxRegularTrips = data["MaxRegularTrips"] # scalar parameter
MinSpeedPercentage = data["MinSpeedPercentage"] # scalar parameter
TotalMail = data["TotalMail"] # scalar parameter
RegularTrips = model.addVar(vtype=gp.GRB.INTEGER, name="RegularTrips")
SpeedTrips = model.addVar(vtype=gp.GRB.INTEGER, name="SpeedTrips")
TotalTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalTrips")

# Constraint: Number of regular boat trips is non-negative and does not exceed the maximum allowed
model.addConstr(0 <= RegularTrips, "RegularTrips_non_negative")
model.addConstr(RegularTrips <= MaxRegularTrips, "RegularTrips_max_limit")

# Since SpeedTrips is already an integer variable, no code is needed to enforce non-negativity
# The Gurobi optimizer enforces the non-negative constraint by default for integer variables.

# Constraint: The number of trips made by regular boats should not exceed the maximum allowed
model.addConstr(RegularTrips <= MaxRegularTrips, name="max_regular_trips_constraint")

# Constraint to ensure at least MinSpeedPercentage of the total trips are made by speed boats
model.addConstr(SpeedTrips >= MinSpeedPercentage * TotalTrips, name="min_speed_boat_trips")

# Define the constraint for total mail delivery by regular and speed boats
model.addConstr(RegularTrips * RegularCapacity + SpeedTrips * SpeedCapacity >= TotalMail, name="total_mail_delivery")

# Define the constraint where TotalTrips is the sum of SpeedTrips and RegularTrips
model.addConstr(TotalTrips == SpeedTrips + RegularTrips, name="TotalTrips_constraint")

model.addConstr(RegularTrips <= MaxRegularTrips, "max_regular_trips_constraint")

# Add constraint to ensure the minimum proportion of trips made by speed boats
model.addConstr(SpeedTrips >= MinSpeedPercentage * TotalTrips, name="min_speed_boat_trips")

# Constraint: Total trips should be the sum of regular and speed boat trips
model.addConstr(TotalTrips == RegularTrips + SpeedTrips, name="total_trips")

# Ensure all mail is delivered constraint
model.addConstr(RegularTrips * RegularCapacity + SpeedTrips * SpeedCapacity >= TotalMail, "mail_delivery")

# Define the objective function
model.setObjective(RegularFuel * RegularTrips + SpeedFuel * SpeedTrips, gp.GRB.MINIMIZE)

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
