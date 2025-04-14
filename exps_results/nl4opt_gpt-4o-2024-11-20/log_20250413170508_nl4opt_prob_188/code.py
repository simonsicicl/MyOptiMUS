import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_188/data.json", "r") as f:
    data = json.load(f)

TaxiCapacity = data["TaxiCapacity"] # scalar parameter
CarCapacity = data["CarCapacity"] # scalar parameter
MaxCarRideProportion = data["MaxCarRideProportion"] # scalar parameter
MinCarRides = data["MinCarRides"] # scalar parameter
MinEmployees = data["MinEmployees"] # scalar parameter
TaxiRides = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TaxiRides")
CarRides = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CarRides")

EmployeeTaxis = model.addVar(vtype=gp.GRB.CONTINUOUS, name="EmployeeTaxis")
model.addConstr(TaxiRides * TaxiCapacity >= EmployeeTaxis, name="employee_taxi_capacity")

# Update variable CarRides to an integer type
CarRides.vtype = gp.GRB.INTEGER

# Add constraint to ensure the proportion of company car rides does not exceed the maximum allowed proportion of total rides
model.addConstr((1 - MaxCarRideProportion) * CarRides <= MaxCarRideProportion * TaxiRides, name="max_car_ride_proportion")

# Add constraint to ensure the total number of company car rides is at least the minimum required
model.addConstr(CarRides >= MinCarRides, name="min_car_rides_constraint")

# Add constraint to ensure sufficient rides to transport at least MinEmployees
model.addConstr(
    TaxiCapacity * TaxiRides + CarCapacity * CarRides >= MinEmployees,
    name="sufficient_transport_constraint"
)

# No code needed, as non-negativity is inherent to the default behavior of the TaxiRides variable (continuous variables in Gurobi are non-negative by default unless contrary bounds are explicitly specified).

# Non-negativity constraint for CarRides
model.addConstr(CarRides >= 0, name="non_negativity_CarRides")

# Add transportation capacity constraint
model.addConstr(TaxiCapacity * TaxiRides + CarCapacity * CarRides >= MinEmployees, name="transportation_capacity")

# Add constraint to ensure company car rides do not exceed the maximum proportion of total rides
model.addConstr(CarRides <= MaxCarRideProportion * (TaxiRides + CarRides), name="max_car_ride_proportion")

# Add constraint to ensure the minimum required number of company car rides is used
model.addConstr(CarRides >= MinCarRides, name="min_car_rides")

# Set objective
model.setObjective(TaxiRides, gp.GRB.MINIMIZE)

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
