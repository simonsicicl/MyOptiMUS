import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_280/data.json", "r") as f:
    data = json.load(f)

BusCapacity = data["BusCapacity"] # scalar parameter
CarCapacity = data["CarCapacity"] # scalar parameter
MinChildren = data["MinChildren"] # scalar parameter
MinCars = data["MinCars"] # scalar parameter
BusesUsed = model.addVar(vtype=gp.GRB.INTEGER, name="BusesUsed")
PersonalCarsUsed = model.addVar(vtype=gp.GRB.INTEGER, name="PersonalCarsUsed")

model.addConstr(BusesUsed >= 0, name="BusesUsed_non_negative")

# Since PersonalCarsUsed is already defined as a non-negative integer variable, no additional constraint is needed
# PersonalCarsUsed >= 0 is inherently enforced by the variable definition

# Add constraint to ensure the total capacity of buses and cars accommodate at least MinChildren
model.addConstr(BusesUsed * BusCapacity + PersonalCarsUsed * CarCapacity >= MinChildren, "min_children_capacity")

# Constraint for more buses than personal cars
model.addConstr(BusesUsed >= PersonalCarsUsed + 1, name="buses_vs_cars_constraint")

# Add constraint to ensure the number of personal cars used is at least the minimum
model.addConstr(PersonalCarsUsed >= MinCars, name="min_personal_cars")

# Add constraint to ensure that the minimum number of personal cars are used
model.addConstr(PersonalCarsUsed >= MinCars, name="min_personal_cars_used")

# Ensure that the minimum number of children are picked up
model.addConstr(BusesUsed * BusCapacity + PersonalCarsUsed * CarCapacity >= MinChildren, name="min_children_pickup")

# Set objective
model.setObjective(BusesUsed + PersonalCarsUsed, gp.GRB.MINIMIZE)

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
