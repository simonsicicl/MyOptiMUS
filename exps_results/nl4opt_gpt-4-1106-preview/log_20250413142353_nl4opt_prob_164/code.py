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
SmallContainers = model.addVar(vtype=gp.GRB.INTEGER, name="SmallContainers")
LargeContainers = model.addVar(vtype=gp.GRB.INTEGER, name="LargeContainers")

# Since the SmallContainers and LargeContainers variables are already defined as integer,
# with the default lower bound of 0 in Gurobi, there is no need to add any additional constraints.
# The non-negativity and integrality are already enforced by their respective variable declarations.

# Constraint: The total number of people required to unload all small containers should not exceed the number of people available
model.addConstr(SmallContainers * SmallUnload <= PeopleAvailable, name="small_containers_unloading")



# Ensure at least MinSmallContainers small containers are used
model.addConstr(SmallContainers >= MinSmallContainers, name="min_small_containers")

# Ensure at least MinLargeContainers large containers are used
model.addConstr(LargeContainers >= MinLargeContainers, name="min_large_containers")

# The total people used for unloading should not exceed the total number of people available
model.addConstr((SmallContainers * SmallUnload) + (LargeContainers * LargeUnload) <= PeopleAvailable, "unloading_capacity")

# Add constraint for the relation between small and large containers
model.addConstr(SmallContainers >= ContainerRatio * LargeContainers, name="container_ratio_constraint")

# Ensure that the minimum number of small containers is used
model.addConstr(SmallContainers >= MinSmallContainers, name="min_small_containers")

model.addConstr(LargeContainers >= MinLargeContainers, name="min_large_containers")

# Set objective
model.setObjective(SmallContainers * SmallCapacity + LargeContainers * LargeCapacity, gp.GRB.MAXIMIZE)

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
