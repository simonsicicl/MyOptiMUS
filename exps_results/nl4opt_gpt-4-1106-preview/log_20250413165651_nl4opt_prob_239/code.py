import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_239/data.json", "r") as f:
    data = json.load(f)

LimousineCapacity = data["LimousineCapacity"] # scalar parameter
BusCapacity = data["BusCapacity"] # scalar parameter
MinimumPeople = data["MinimumPeople"] # scalar parameter
MinimumLimousinePercentage = data["MinimumLimousinePercentage"] # scalar parameter
NumLimousines = model.addVar(vtype=gp.GRB.INTEGER, name="NumLimousines")
NumBuses = model.addVar(vtype=gp.GRB.INTEGER, name="NumBuses")

# NumLimousines is already defined as an integer variable; just need to ensure it is non-negative
model.addConstr(NumLimousines >= 0, name="non_negative_limousines")

# Since NumBuses is already defined as a non-negative integer variable, no additional constraint is required.

# At least MinimumPeople must be transported
model.addConstr(NumLimousines * LimousineCapacity + NumBuses * BusCapacity >= MinimumPeople, name="minimum_people_transported")

# Add constraint to ensure at least MinimumLimousinePercentage of the total vehicles are limousines
model.addConstr(NumLimousines >= MinimumLimousinePercentage * (NumLimousines + NumBuses), name="limousine_min_percentage")

# Ensure minimum number of people to be transported is met
model.addConstr(NumLimousines * LimousineCapacity + NumBuses * BusCapacity >= MinimumPeople, name="min_people_transported")

# Ensure minimum percentage of vehicles that are limousines is met
model.addConstr(NumLimousines >= MinimumLimousinePercentage * (NumLimousines + NumBuses), name="limousine_percentage")

# Set objective
model.setObjective(NumLimousines + NumBuses, gp.GRB.MINIMIZE)

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
