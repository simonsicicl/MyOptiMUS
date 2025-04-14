import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_179/data.json", "r") as f:
    data = json.load(f)

TiresPlane = data["TiresPlane"] # scalar parameter
CostPlane = data["CostPlane"] # scalar parameter
TiresTruck = data["TiresTruck"] # scalar parameter
CostTruck = data["CostTruck"] # scalar parameter
MinTires = data["MinTires"] # scalar parameter
Budget = data["Budget"] # scalar parameter
NumberOfPlaneTrips = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfPlaneTrips")
NumberOfTruckTrips = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfTruckTrips")

# Constraint: Number of plane trips must be non-negative
model.addConstr(NumberOfPlaneTrips >= 0, name="non_negative_plane_trips")

# No code needed since the variable NumberOfTruckTrips is already defined as an integer which implies it cannot take negative values.

# Constraint: At least MinTires tires must be transported in total
model.addConstr(NumberOfPlaneTrips * TiresPlane + NumberOfTruckTrips * TiresTruck >= MinTires, name="MinTires_Transport")

# Define the budget constraint for the total cost of plane and truck trips
model.addConstr(CostPlane * NumberOfPlaneTrips + CostTruck * NumberOfTruckTrips <= Budget, name="budget_constraint")

# Add constraint to ensure plane trips do not exceed truck trips
model.addConstr(NumberOfPlaneTrips <= NumberOfTruckTrips, name="plane_truck_trip_limit")

# Ensure at least the minimum required tires are transported
model.addConstr(TiresPlane * NumberOfPlaneTrips + TiresTruck * NumberOfTruckTrips >= MinTires, name="min_tires_transported")

# Ensure the total cost does not exceed the available budget
total_cost = CostPlane * NumberOfPlaneTrips + CostTruck * NumberOfTruckTrips
model.addConstr(total_cost <= Budget, name="budget_constraint")

# Set objective
model.setObjective(NumberOfPlaneTrips + NumberOfTruckTrips, gp.GRB.MINIMIZE)

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
