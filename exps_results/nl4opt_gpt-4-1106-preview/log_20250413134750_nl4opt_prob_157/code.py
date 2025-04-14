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
NumberOfContainers = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfContainers")
NumberOfTrucks = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfTrucks")

# Add constraint to ensure number of containers used is non-negative
model.addConstr(NumberOfContainers >= 0, "NumberOfContainers_nonnegativity")

# Since NumberOfTrucks is already defined as a non-negative integer, no additional constraint is needed
# The non-negativity constraint is inherently applied through the variable type definition

# Constraint: Number of trucks used is at most TruckContainerRatio times the number of containers used
model.addConstr(NumberOfTrucks <= TruckContainerRatio * NumberOfContainers, name="truck_to_container_ratio")

ContainerCapacity = data["ContainerCapacity"] # scalar parameter
TruckCapacity = data["TruckCapacity"] # scalar parameter
MinimumUnits = data["MinimumUnits"] # scalar parameter

# Constraint for minimum units of oil to be sent to the port
model.addConstr(ContainerCapacity * NumberOfContainers + TruckCapacity * NumberOfTrucks >= MinimumUnits, name="minimum_oil_units_to_port")

# At least a minimum number of containers need to be used
model.addConstr(NumberOfContainers >= MinimumContainers, name="min_containers")

# Ensure that at least the minimum total units of oil is transported to the port
model.addConstr(NumberOfContainers * ContainerCapacity + NumberOfTrucks * TruckCapacity >= MinimumUnits, "min_oil_transportation")

model.addConstr(NumberOfContainers >= MinimumContainers, name="min_containers_constraint")

# Maintain the maximum ratio of number of trucks to number of containers constraint
model.addConstr(NumberOfTrucks <= NumberOfContainers * TruckContainerRatio, name="max_truck_container_ratio")

# Set objective
model.setObjective(NumberOfContainers + NumberOfTrucks, gp.GRB.MINIMIZE)

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
