import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_156/data.json", "r") as f:
    data = json.load(f)

VanCapacity = data["VanCapacity"] # scalar parameter
TruckCapacity = data["TruckCapacity"] # scalar parameter
MinPairs = data["MinPairs"] # scalar parameter
NumVans = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumVans")
NumTrucks = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumTrucks")

# Add constraint for minimum total pairs of shoes delivered
model.addConstr(
    NumVans * VanCapacity + NumTrucks * TruckCapacity >= MinPairs,
    name="min_total_pairs"
)

# Add constraint: Number of trucks used is less than or equal to the number of vans used
model.addConstr(NumTrucks <= NumVans, name="num_trucks_leq_num_vans")

# No additional code required because the variable "NumVans" is already non-negative due to its default lower bound (0) in Gurobi.

# Add constraint to ensure total capacity of vans and trucks meets or exceeds minimum shoe supply demands
model.addConstr(NumVans * VanCapacity + NumTrucks * TruckCapacity >= MinPairs, name="capacity_constraint")

# Add constraint ensuring the number of trucks does not exceed the number of vans
model.addConstr(NumTrucks <= NumVans, name="trucks_not_exceed_vans")

# Set objective
model.setObjective(NumVans, gp.GRB.MINIMIZE)

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
