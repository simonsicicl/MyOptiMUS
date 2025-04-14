import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_193/data.json", "r") as f:
    data = json.load(f)

C = data["C"] # scalar parameter
Pc = data["Pc"] # scalar parameter
B = data["B"] # scalar parameter
Pb = data["Pb"] # scalar parameter
MinE = data["MinE"] # scalar parameter
MaxBuses = data["MaxBuses"] # scalar parameter
NumberOfCars = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfCars")
NumberOfBuses = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfBuses")

model.addConstr(NumberOfCars >= 0, name="non_negative_cars")

# The number of buses must be non-negative. Since the variable is defined as an integer, no need to add a constraint.

# At least MinE employees need to be transported using cars and buses
model.addConstr(C * NumberOfCars + B * NumberOfBuses >= MinE, name="min_employees_transported")

model.addConstr(NumberOfBuses <= MaxBuses, name="max_buses_constraint")

# Ensure that the minimum number of employees are transported
model.addConstr(NumberOfCars * C + NumberOfBuses * B >= MinE, name="min_employee_transportation")

# Ensure that the maximum number of buses to be used is not exceeded
model.addConstr(NumberOfBuses <= MaxBuses, name="max_buses_constraint")

# Set objective
model.setObjective(NumberOfCars * Pc + NumberOfBuses * Pb, gp.GRB.MINIMIZE)

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
