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
NumberOfSedans = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfSedans")
NumberOfBuses = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfBuses")

# The variable "NumberOfSedans" is non-negative by default since it is a continuous variable.

# Non-negativity of the NumberOfBuses is ensured by the default lower bound of 0 in gurobipy variables.

# Add pollution limit constraint
model.addConstr(
    NumberOfSedans * SedanPollution + NumberOfBuses * BusPollution <= MaxPollution,
    name="pollution_limit"
)

# Add constraint for total capacity of sedans and buses
model.addConstr(
    NumberOfSedans * SedanCapacity + NumberOfBuses * BusCapacity >= MinCustomers,
    name="total_capacity_constraint"
)

# Add constraint for minimum number of customers served per day
model.addConstr(SedanCapacity * NumberOfSedans + BusCapacity * NumberOfBuses >= MinCustomers, name="min_customers_served")

# Add pollution limit constraint
model.addConstr(SedanPollution * NumberOfSedans + BusPollution * NumberOfBuses <= MaxPollution, name="pollution_limit")

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
