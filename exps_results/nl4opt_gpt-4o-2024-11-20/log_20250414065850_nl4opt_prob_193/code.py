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
NumberOfCars = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfCars")
NumberOfBuses = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfBuses")

# No additional code needed since the variable "NumberOfCars" is already defined as non-negative due to its type being CONTINUOUS in gurobipy.

# The variable "NumberOfBuses" is already defined as non-negative (continuous variables in Gurobi are non-negative by default), so no additional constraint is needed.

# Add constraint for minimum employees transported
model.addConstr(C * NumberOfCars + B * NumberOfBuses >= MinE, name="min_employees_constraint")

# Add constraint to enforce that the number of buses does not exceed MaxBuses
model.addConstr(NumberOfBuses <= MaxBuses, name="bus_limit_constraint")

# Add constraint to ensure that the total number of employees transported meets or exceeds the minimum required
model.addConstr(C * NumberOfCars + B * NumberOfBuses >= MinE, name="employee_transport_minimum")

# Add the constraint to restrict the number of buses used to the maximum allowed
model.addConstr(NumberOfBuses <= MaxBuses, name="bus_limit_constraint")

# Set objective
model.setObjective(Pc * NumberOfCars + Pb * NumberOfBuses, gp.GRB.MINIMIZE)

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
