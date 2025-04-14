import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_183/data.json", "r") as f:
    data = json.load(f)

BalloonCapacity = data["BalloonCapacity"] # scalar parameter
GondolaCapacity = data["GondolaCapacity"] # scalar parameter
BalloonPollution = data["BalloonPollution"] # scalar parameter
GondolaPollution = data["GondolaPollution"] # scalar parameter
MaxBalloons = data["MaxBalloons"] # scalar parameter
MinVisitors = data["MinVisitors"] # scalar parameter
BalloonRides = model.addVar(vtype=gp.GRB.CONTINUOUS, name="BalloonRides")
GondolaTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="GondolaTrips")

# Ensure the number of hot-air balloon rides is non-negative
model.addConstr(BalloonRides >= 0, name="non_negative_balloon_rides")

# No additional code needed because Gurobi variables are non-negative by default unless explicitly defined with lower bounds less than zero.

# Add constraint to limit the number of hot-air balloon rides
model.addConstr(BalloonRides <= MaxBalloons, name="max_balloon_rides")

# Add visitor transportation constraint
model.addConstr(
    BalloonRides * BalloonCapacity + GondolaTrips * GondolaCapacity >= MinVisitors,
    name="visitor_transportation"
)

# Add constraint to ensure the minimum number of visitors are transported
model.addConstr(
    BalloonCapacity * BalloonRides + GondolaCapacity * GondolaTrips >= MinVisitors,
    name="min_visitors_transport"
)

# Add constraint to ensure the number of hot-air balloon rides does not exceed the maximum allowed
model.addConstr(BalloonRides <= MaxBalloons, name="max_balloon_rides")

# Set objective
model.setObjective(BalloonPollution * BalloonRides + GondolaPollution * GondolaTrips, gp.GRB.MINIMIZE)

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
