import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_153/data.json", "r") as f:
    data = json.load(f)

OldVanCapacity = data["OldVanCapacity"] # scalar parameter
NewVanCapacity = data["NewVanCapacity"] # scalar parameter
OldVanPollution = data["OldVanPollution"] # scalar parameter
NewVanPollution = data["NewVanPollution"] # scalar parameter
MinBottles = data["MinBottles"] # scalar parameter
MaxNewVans = data["MaxNewVans"] # scalar parameter
NumberOfOldVans = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfOldVans")
NumberOfNewVans = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfNewVans")

# Since the variable "NumberOfOldVans" is already defined with non-negativity enforced as it is continuous, no constraint code is needed.

# The variable "NumberOfNewVans" is already defined as non-negative because it is continuous and Gurobi enforces non-negativity by default for such variables.

# Add constraint for delivering at least MinBottles
model.addConstr(NumberOfOldVans * OldVanCapacity + NumberOfNewVans * NewVanCapacity >= MinBottles, name="min_bottles_constraint")

# Add constraint to ensure the number of new vans used does not exceed the maximum allowable number
model.addConstr(NumberOfNewVans <= MaxNewVans, name="max_new_vans_constraint")

# Add constraint to ensure total capacity of vans satisfies the minimum quantity of soda bottles required
model.addConstr(
    NumberOfOldVans * OldVanCapacity + NumberOfNewVans * NewVanCapacity >= MinBottles,
    name="van_capacity_constraint"
)

# Add constraint to ensure the number of new vans used does not exceed the maximum allowed
model.addConstr(NumberOfNewVans <= MaxNewVans, name="max_new_vans_constraint")

# As NumberOfOldVans and NumberOfNewVans are already defined as continuous variables, and continuous variables in Gurobi are non-negative by default, no code is required.

# Change the variable types to integer as they need to be integers
NumberOfOldVans.vtype = gp.GRB.INTEGER
NumberOfNewVans.vtype = gp.GRB.INTEGER

# Set objective
model.setObjective(NumberOfOldVans * OldVanPollution + NumberOfNewVans * NewVanPollution, gp.GRB.MINIMIZE)

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
