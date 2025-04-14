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
NumberOfBuses = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfBuses")
NumberOfCars = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfCars")

# No additional code needed since the integrality and non-negativity of NumberOfBuses is inherently ensured by its variable definition as an INTEGER type in gurobipy.

# No code is needed because the non-negativity constraint is automatically enforced due to the default non-negative domain of continuous variables in Gurobi.

# Add total capacity constraint for buses and cars
model.addConstr(NumberOfBuses * BusCapacity + NumberOfCars * CarCapacity >= MinChildren, 
                name="total_capacity_constraint")

# Add constraint: The number of buses used must always be greater than the number of personal cars used.
model.addConstr(NumberOfBuses >= NumberOfCars + 1, name="buses_greater_than_cars")

# Add constraint to enforce a minimum number of personal cars
model.addConstr(NumberOfCars >= MinCars, name="min_personal_cars")

# Add bus and car capacity constraint
model.addConstr(BusCapacity * NumberOfBuses + CarCapacity * NumberOfCars >= MinChildren, name="capacity_constraint")

# Add the constraint to ensure the number of personal cars meets or exceeds the minimum requirement
model.addConstr(NumberOfCars >= MinCars, name="minimum_cars_requirement")

# Set objective
model.setObjective(NumberOfBuses + NumberOfCars, gp.GRB.MINIMIZE)

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
