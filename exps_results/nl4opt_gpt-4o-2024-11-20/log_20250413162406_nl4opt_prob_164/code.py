import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_164/data.json", "r") as f:
    data = json.load(f)

SmallCapacity = data["SmallCapacity"] # scalar parameter
LargeCapacity = data["LargeCapacity"] # scalar parameter
SmallUnload = data["SmallUnload"] # scalar parameter
LargeUnload = data["LargeUnload"] # scalar parameter
ContainerRatio = data["ContainerRatio"] # scalar parameter
MinSmallContainers = data["MinSmallContainers"] # scalar parameter
MinLargeContainers = data["MinLargeContainers"] # scalar parameter
PeopleAvailable = data["PeopleAvailable"] # scalar parameter
SmallContainers = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SmallContainers")
LargeContainers = model.addVar(vtype=gp.GRB.CONTINUOUS, name="LargeContainers")

# SmallContainers and LargeContainers integer constraints
SmallContainers.vtype = gp.GRB.INTEGER
LargeContainers.vtype = gp.GRB.INTEGER

# SmallContainers and LargeContainers non-negativity constraints
model.addConstr(SmallContainers >= 0, name="SmallContainers_non_negative")
model.addConstr(LargeContainers >= 0, name="LargeContainers_non_negative")

# Add constraint to ensure total unloading workforce does not exceed available people
model.addConstr(
    (SmallContainers * SmallUnload) + (LargeContainers * LargeUnload) <= PeopleAvailable,
    name="unloading_workforce_limit"
)

# Add constraint to enforce SmallContainers equals ContainerRatio times LargeContainers
model.addConstr(SmallContainers == ContainerRatio * LargeContainers, name="container_ratio_constraint")

# Add minimum small containers constraint
model.addConstr(SmallContainers >= MinSmallContainers, name="min_small_containers")

# Ensure the minimum number of large containers constraint
model.addConstr(LargeContainers >= MinLargeContainers, name="min_large_containers")

# Add labor availability constraint ensuring total unloading labor does not exceed available people
model.addConstr(
    SmallUnload * SmallContainers + LargeUnload * LargeContainers <= PeopleAvailable,
    name="labor_availability"
)

# Add constraint to ensure the minimum number of small containers is used
model.addConstr(SmallContainers >= MinSmallContainers, name="min_small_containers")

model.addConstr(LargeContainers >= MinLargeContainers, name="min_large_containers")

# Add container ratio constraint
model.addConstr(SmallContainers >= ContainerRatio * LargeContainers, name="container_ratio_constraint")

# Set objective
model.setObjective((SmallCapacity * SmallContainers) + (LargeCapacity * LargeContainers), gp.GRB.MAXIMIZE)

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
