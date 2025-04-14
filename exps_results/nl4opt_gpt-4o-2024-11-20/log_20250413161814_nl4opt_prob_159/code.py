import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_159/data.json", "r") as f:
    data = json.load(f)

TruckCapacity = data["TruckCapacity"] # scalar parameter
TruckCost = data["TruckCost"] # scalar parameter
VanCapacity = data["VanCapacity"] # scalar parameter
VanCost = data["VanCost"] # scalar parameter
MinPatties = data["MinPatties"] # scalar parameter
Budget = data["Budget"] # scalar parameter
TrucksUsed = model.addVar(vtype=gp.GRB.INTEGER, name="TrucksUsed")
VansUsed = model.addVar(vtype=gp.GRB.INTEGER, name="VansUsed")

# No additional code needed since non-negativity for TrucksUsed is automatically handled by Gurobi's non-negative domain for integer variables.

# No code needed since the integrality and non-negativity of variables are automatically handled internally by Gurobi when defining the variable using `gp.GRB.INTEGER`.

# Add constraint: The number of trucks must not exceed the number of vans
model.addConstr(TrucksUsed <= VansUsed, name="trucks_vans_constraint")

# Add constraint to ensure at least MinPatties are shipped
model.addConstr(TruckCapacity * TrucksUsed + VanCapacity * VansUsed >= MinPatties, name="min_patties_shipped")

# Add budget constraint for truck and van usage
model.addConstr(TruckCost * TrucksUsed + VanCost * VansUsed <= Budget, name="budget_constraint")

# Add shipping capacity constraint
model.addConstr(TruckCapacity * TrucksUsed + VanCapacity * VansUsed >= MinPatties, name="shipping_capacity")

# Add budget constraint for total cost of trips
model.addConstr(TruckCost * TrucksUsed + VanCost * VansUsed <= Budget, name="budget_constraint")

# Set objective
model.setObjective(TrucksUsed + VansUsed, gp.GRB.MINIMIZE)

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
