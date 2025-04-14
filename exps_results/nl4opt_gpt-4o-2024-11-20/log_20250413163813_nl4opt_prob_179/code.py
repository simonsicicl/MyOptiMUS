import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_179/data.json", "r") as f:
    data = json.load(f)

TiresPlane = data["TiresPlane"] # scalar parameter
CostPlane = data["CostPlane"] # scalar parameter
TiresTruck = data["TiresTruck"] # scalar parameter
CostTruck = data["CostTruck"] # scalar parameter
MinTires = data["MinTires"] # scalar parameter
Budget = data["Budget"] # scalar parameter
PlaneTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PlaneTrips")
TruckTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TruckTrips")

# The non-negativity constraint for "PlaneTrips" is already satisfied as it is defined as a continuous variable with default lower bound of 0 in Gurobi.

# No code is needed: Gurobi variables by default have non-negativity constraints unless explicitly set otherwise.

# Add constraint to ensure total tires transported is at least MinTires
model.addConstr(
    PlaneTrips * TiresPlane + TruckTrips * TiresTruck >= MinTires, 
    name="min_tires_constraint"
)

# Add budget constraint for transportation costs
model.addConstr(CostPlane * PlaneTrips + CostTruck * TruckTrips <= Budget, name="transport_budget")

# Add constraint ensuring the number of plane trips does not exceed the number of truck trips
model.addConstr(PlaneTrips <= TruckTrips, name="plane_trips_limit")

# Add constraint to ensure total tires delivered meets the minimum requirement
model.addConstr(TiresPlane * PlaneTrips + TiresTruck * TruckTrips >= MinTires, name="min_tires_requirement")

# Add transportation cost budget constraint
model.addConstr(
    CostPlane * PlaneTrips + CostTruck * TruckTrips <= Budget, 
    name="transportation_budget_constraint"
)

# Set objective
model.setObjective(PlaneTrips + TruckTrips, gp.GRB.MINIMIZE)

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
