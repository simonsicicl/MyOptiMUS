import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_278/data.json", "r") as f:
    data = json.load(f)

SedanCapacity = data["SedanCapacity"] # scalar parameter
SedanPollution = data["SedanPollution"] # scalar parameter
BusCapacity = data["BusCapacity"] # scalar parameter
BusPollution = data["BusPollution"] # scalar parameter
MaxPollution = data["MaxPollution"] # scalar parameter
MinCustomers = data["MinCustomers"] # scalar parameter
NumberOfSedans = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfSedans")
NumberOfBuses = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfBuses")

# As the variable NumberOfSedans is already set to be an INTEGER in its definition code,
# and non-negativity is the default lower bound for Gurobi integer variables,
# no additional code is necessary for this constraint.

# Since NumberOfBuses is already defined as an integer variable, no constraint is needed to ensure its non-negativity
# Gurobi enforces that integer variables are non-negative by default, hence no additional code is necessary

# Add pollution constraint
model.addConstr(NumberOfSedans * SedanPollution + NumberOfBuses * BusPollution <= MaxPollution, name="total_pollution")

# Add constraint to ensure total capacity of sedans and buses meets the minimum customers requirement for profit
model.addConstr(NumberOfSedans * SedanCapacity + NumberOfBuses * BusCapacity >= MinCustomers, name="min_customers_capacity")

# Ensure the combined capacity of sedans and buses meets the minimum number of customers to be served per day for profit
model.addConstr(NumberOfSedans * SedanCapacity + NumberOfBuses * BusCapacity >= MinCustomers, "capacity_constraint")

# Ensure the pollution from the sedans and buses does not exceed the maximum allowed pollution units per day
model.addConstr(NumberOfSedans * SedanPollution + NumberOfBuses * BusPollution <= MaxPollution, name="max_pollution_constraint")

# Set objective
model.setObjective(NumberOfSedans + NumberOfBuses, gp.GRB.MINIMIZE)

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
