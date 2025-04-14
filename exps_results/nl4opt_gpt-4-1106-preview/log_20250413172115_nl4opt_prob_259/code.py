import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_259/data.json", "r") as f:
    data = json.load(f)

EscalatorRate = data["EscalatorRate"] # scalar parameter
ElevatorRate = data["ElevatorRate"] # scalar parameter
EscalatorSpace = data["EscalatorSpace"] # scalar parameter
ElevatorSpace = data["ElevatorSpace"] # scalar parameter
CapacityMinimum = data["CapacityMinimum"] # scalar parameter
EscalatorElevatorRatio = data["EscalatorElevatorRatio"] # scalar parameter
ElevatorMinNumber = data["ElevatorMinNumber"] # scalar parameter
EscalatorNumber = model.addVar(vtype=gp.GRB.INTEGER, name="EscalatorNumber")
ElevatorNumber = model.addVar(vtype=gp.GRB.INTEGER, name="ElevatorNumber")

# Add minimum transport capacity constraint
model.addConstr(EscalatorNumber * EscalatorRate + ElevatorNumber * ElevatorRate >= CapacityMinimum, name="min_transport_capacity")

EscalatorNumber >= EscalatorElevatorRatio * ElevatorNumber
model.addConstr(EscalatorNumber >= EscalatorElevatorRatio * ElevatorNumber, name="escalator_elevator_ratio")

ElevatorMinNumber = data["ElevatorMinNumber"] # scalar parameter
model.addConstr(ElevatorNumber >= ElevatorMinNumber, name="min_elevator_constraint")

# Since the variable "EscalatorNumber" is already guaranteed to be non-negative by its type definition,
# no additional constraint is necessary.
# However, if we needed to explicitly add a constraint, we would do the following:
# model.addConstr(EscalatorNumber >= 0, name="non_negative_escalators")

# Ensure that the number of elevators is non-negative
model.addConstr(ElevatorNumber >= 0, name="elevator_non_negativity")

# Transport capacity constraint
model.addConstr(EscalatorNumber * EscalatorRate + ElevatorNumber * ElevatorRate >= CapacityMinimum, name="transport_capacity")

# Add constraint for the number of escalators to be at least a certain ratio of the number of elevators
model.addConstr(EscalatorNumber >= EscalatorElevatorRatio * ElevatorNumber, name="escalator_to_elevator_ratio")

# Add constraint for the minimum number of elevators
model.addConstr(ElevatorNumber >= ElevatorMinNumber, "min_elevators")

# Set objective function
model.setObjective(EscalatorNumber * EscalatorSpace + ElevatorNumber * ElevatorSpace, gp.GRB.MINIMIZE)

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
