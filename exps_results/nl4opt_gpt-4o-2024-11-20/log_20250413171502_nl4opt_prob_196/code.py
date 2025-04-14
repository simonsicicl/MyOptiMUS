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
NumberOfLargeShips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfLargeShips")
NumberOfSmallShips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfSmallShips")

# No code is needed for this constraint since the variable `NumberOfLargeShips` is already defined as non-negative,
# which is the default for continuous variables in Gurobi.

# The non-negativity constraint is inherently satisfied as the variable "NumberOfSmallShips" is declared to be non-negative. No additional constraint is needed.

# Add constraint: Number of large ships cannot exceed the number of small ships
model.addConstr(NumberOfLargeShips <= NumberOfSmallShips, name="large_vs_small_ships")

# Add constraint ensuring the total number of containers transported meets or exceeds the minimum required
model.addConstr(NumberOfLargeShips * LargeShipCapacity + NumberOfSmallShips * SmallShipCapacity >= MinContainers, name="MinContainersConstraint")

# Ensure the total shipping capacity meets or exceeds the minimum container requirement
model.addConstr(
    LargeShipCapacity * NumberOfLargeShips + SmallShipCapacity * NumberOfSmallShips >= MinContainers,
    name="min_container_requirement"
)

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
