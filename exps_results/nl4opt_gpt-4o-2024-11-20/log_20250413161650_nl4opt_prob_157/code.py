import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_157/data.json", "r") as f:
    data = json.load(f)

ContainerCapacity = data["ContainerCapacity"] # scalar parameter
TruckCapacity = data["TruckCapacity"] # scalar parameter
TruckContainerRatio = data["TruckContainerRatio"] # scalar parameter
MinimumUnits = data["MinimumUnits"] # scalar parameter
MinimumContainers = data["MinimumContainers"] # scalar parameter
NumContainers = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumContainers")
NumTrucks = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumTrucks")

# The non-negativity constraint for NumContainers is implicitly satisfied by Gurobi's default lower bound of zero for continuous variables.

# No additional code needed because Gurobi variables are non-negative by default unless explicitly defined with lower bounds less than zero.

# Add constraint to ensure the number of trucks used is at most TruckContainerRatio times the number of containers used
model.addConstr(NumTrucks <= TruckContainerRatio * NumContainers, name="truck_container_ratio")

# Add constraint to ensure the total oil transported meets the minimum required units
model.addConstr(NumContainers * ContainerCapacity + NumTrucks * TruckCapacity >= MinimumUnits, name="minimum_transportation_constraint")

# Ensure at least the minimum number of containers are used
model.addConstr(NumContainers >= MinimumContainers, name="min_containers")

# Add constraint to ensure containers and trucks have sufficient capacity
model.addConstr(
    NumContainers * ContainerCapacity + NumTrucks * TruckCapacity >= MinimumUnits,
    name="capacity_constraint"
)

# Add constraint to ensure the number of trucks does not exceed TruckContainerRatio multiplied by the number of containers
model.addConstr(NumTrucks <= TruckContainerRatio * NumContainers, name="truck_to_container_ratio")

# Adjusting the integrality of NumContainers to INTEGER
NumContainers.vtype = gp.GRB.INTEGER

# Adding the minimum containers constraint
model.addConstr(NumContainers >= MinimumContainers, name="min_containers")

# Set objective
model.setObjective(NumContainers + NumTrucks, gp.GRB.MINIMIZE)

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
