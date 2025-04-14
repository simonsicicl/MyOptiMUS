import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_198/data.json", "r") as f:
    data = json.load(f)

VanCapacity = data["VanCapacity"] # scalar parameter
CarCapacity = data["CarCapacity"] # scalar parameter
MinimumVoters = data["MinimumVoters"] # scalar parameter
MaxVansRatio = data["MaxVansRatio"] # scalar parameter
NumberOfVans = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfVans")
NumberOfCars = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfCars")

# Add non-negativity constraint for the number of vans
model.addConstr(NumberOfVans >= 0, name="non_negativity_vans")

# Add constraint for non-negative number of cars
model.addConstr(NumberOfCars >= 0, name="non_negative_cars")

# Add constraint for minimum number of voters transported
model.addConstr(NumberOfVans * VanCapacity + NumberOfCars * CarCapacity >= MinimumVoters, name="min_voters_transport")

# At most MaxVansRatio of the total number of vehicles can be vans constraint
model.addConstr(NumberOfVans <= MaxVansRatio * (NumberOfVans + NumberOfCars), name="max_vans_ratio")

# Ensure the total capacity meets the minimum voter requirement
model.addConstr(VanCapacity * NumberOfVans + CarCapacity * NumberOfCars >= MinimumVoters, "min_voters_requirement")

# Ensure the ratio of vans to the total number of vehicles does not exceed the maximum proportion
model.addConstr(NumberOfVans <= MaxVansRatio * (NumberOfVans + NumberOfCars), name="max_vans_ratio_constraint")

# Define variables
NumberOfVans = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfVans")
NumberOfCars = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfCars")

# Set objective
model.setObjective(NumberOfVans + NumberOfCars, gp.GRB.MINIMIZE)

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
