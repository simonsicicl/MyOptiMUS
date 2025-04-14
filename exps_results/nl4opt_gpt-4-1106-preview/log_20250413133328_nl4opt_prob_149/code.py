import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_149/data.json", "r") as f:
    data = json.load(f)

VanCapacity = data["VanCapacity"] # scalar parameter
TruckCapacity = data["TruckCapacity"] # scalar parameter
VanCost = data["VanCost"] # scalar parameter
TruckCost = data["TruckCost"] # scalar parameter
MinBoxes = data["MinBoxes"] # scalar parameter
Budget = data["Budget"] # scalar parameter
VanTrips = model.addVar(vtype=gp.GRB.INTEGER, name="VanTrips")
TruckTrips = model.addVar(vtype=gp.GRB.INTEGER, name="TruckTrips")

model.addConstr(VanTrips >= 0, name="van_trips_non_negative")

# Since TruckTrips is already defined as an integer variable, we just need to add a constraint to ensure it is non-negative
model.addConstr(TruckTrips >= 0, name="non_negative_truck_trips")

# Add constraint for total boxes transported to be at least the minimum required number of boxes
model.addConstr(VanTrips * VanCapacity + TruckTrips * TruckCapacity >= MinBoxes, name="min_boxes")

# Ensure total cost does not exceed budget
model.addConstr(VanCost * VanTrips + TruckCost * TruckTrips <= Budget, name="budget_constraint")

model.addConstr(VanTrips - TruckTrips >= 1, name="van_over_truck_trips")

# Ensure vans and trucks transport at least the minimum number of boxes required
model.addConstr(VanTrips * VanCapacity + TruckTrips * TruckCapacity >= MinBoxes, name="min_boxes_transport")

# Add constraint for the total cost of vans and trucks not to exceed the budget
model.addConstr(VanTrips * VanCost + TruckTrips * TruckCost <= Budget, name="budget_constraint")

# Set objective
model.setObjective(VanTrips + TruckTrips, gp.GRB.MINIMIZE)

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
