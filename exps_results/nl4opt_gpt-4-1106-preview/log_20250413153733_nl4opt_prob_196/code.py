import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_196/data.json", "r") as f:
    data = json.load(f)

LargeShipCapacity = data["LargeShipCapacity"] # scalar parameter
SmallShipCapacity = data["SmallShipCapacity"] # scalar parameter
MinContainers = data["MinContainers"] # scalar parameter
NumberOfLargeShips = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfLargeShips")
NumberOfSmallShips = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfSmallShips")
TotalNumberOfContainers = model.addVar(vtype=gp.GRB.INTEGER, name="TotalNumberOfContainers")

# Add non-negativity constraint for the number of large ships
model.addConstr(NumberOfLargeShips >= 0, name="nonneg_large_ships")

# Constraint: The number of small ships must be non-negative
model.addConstr(NumberOfSmallShips >= 0, name="non_negative_small_ships")

model.addConstr(NumberOfLargeShips <= NumberOfSmallShips, name="large_ships_leq_small_ships")

# Ensure that the total number of containers transported is at least the minimum required
model.addConstr(TotalNumberOfContainers >= MinContainers, name="min_containers_constraint")

# Constraint for the total number of containers transported by the fleet
model.addConstr(TotalNumberOfContainers == NumberOfLargeShips * LargeShipCapacity + NumberOfSmallShips * SmallShipCapacity, name="total_containers")

# Ensure that the total capacity of the ships meets or exceeds the minimum number of containers required
model.addConstr(LargeShipCapacity * NumberOfLargeShips + SmallShipCapacity * NumberOfSmallShips >= MinContainers, name="capacity_constraint")

# Set objective
model.setObjective(NumberOfLargeShips + NumberOfSmallShips, gp.GRB.MINIMIZE)

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
