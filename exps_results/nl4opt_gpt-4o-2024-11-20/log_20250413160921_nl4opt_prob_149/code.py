import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_149/data.json", "r") as f:
    data = json.load(f)

VanCapacity = data["VanCapacity"] # scalar parameter
TruckCapacity = data["TruckCapacity"] # scalar parameter
VanCost = data["VanCost"] # scalar parameter
TruckCost = data["TruckCost"] # scalar parameter
MinBoxes = data["MinBoxes"] # scalar parameter
Budget = data["Budget"] # scalar parameter
VanTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="VanTrips")
TruckTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TruckTrips")

# No code is needed: Gurobi variables by default satisfy non-negativity for continuous variables unless specified otherwise.

# Add transportation constraints
model.addConstr(VanTrips >= 0, name="nonnegativity_van")
model.addConstr(TruckTrips >= 0, name="nonnegativity_truck")
model.addConstr(VanCapacity * VanTrips + TruckCapacity * TruckTrips >= MinBoxes, name="capacity_requirement")
model.addConstr(VanCost * VanTrips + TruckCost * TruckTrips <= Budget, name="budget_constraint")

# Add constraint to ensure total boxes transported meets minimum required boxes
model.addConstr(VanTrips * VanCapacity + TruckTrips * TruckCapacity >= MinBoxes, name="min_boxes_constraint")

# Add transportation cost constraint
model.addConstr(VanCost * VanTrips + TruckCost * TruckTrips <= Budget, name="transportation_cost")

# Add constraint: Trips made using vans must be at least one greater than trips made using trucks
model.addConstr(VanTrips >= TruckTrips + 1, name="van_vs_truck_trips")

# Add constraint to ensure the total number of boxes transported meets at least the minimum required
model.addConstr(
    VanCapacity * VanTrips + TruckCapacity * TruckTrips >= MinBoxes,
    name="min_boxes_constraint"
)

# Add transportation cost budget constraint
model.addConstr(VanCost * VanTrips + TruckCost * TruckTrips <= Budget, name="transportation_budget_constraint")

# Set objective
model.setObjective(VanTrips + TruckTrips, gp.GRB.MINIMIZE)

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
