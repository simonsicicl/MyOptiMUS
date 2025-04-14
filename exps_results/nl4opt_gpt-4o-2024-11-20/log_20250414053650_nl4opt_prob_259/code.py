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
NumberOfEscalators = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfEscalators")
NumberOfElevators = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfElevators")

# Add transport capacity constraint
model.addConstr(NumberOfEscalators * EscalatorRate + NumberOfElevators * ElevatorRate >= CapacityMinimum, name="transport_capacity")

# Add constraint to ensure the number of escalators is at least EscalatorElevatorRatio times the number of elevators
model.addConstr(NumberOfEscalators >= EscalatorElevatorRatio * NumberOfElevators, name="escalator_elevator_ratio")

# Add constraint to ensure the number of elevators is at least the minimum required
model.addConstr(NumberOfElevators >= ElevatorMinNumber, name="min_elevators_constraint")

# The non-negativity constraint is inherently satisfied as the variable "NumberOfEscalators" is continuous, and continuous variables in Gurobi are non-negative by default.

# Add non-negativity constraint for the NumberOfElevators variable
model.addConstr(NumberOfElevators >= 0, name="non_negativity_elevators")

# Add transport capacity constraint
model.addConstr(EscalatorRate * NumberOfEscalators + ElevatorRate * NumberOfElevators >= CapacityMinimum, name="transport_capacity")

# Add escalator to elevator ratio constraint
model.addConstr(NumberOfEscalators >= EscalatorElevatorRatio * NumberOfElevators, name="escalator_to_elevator_ratio")

# Add the constraint to ensure the minimum number of elevators is met
model.addConstr(NumberOfElevators >= ElevatorMinNumber, name="min_elevators_constraint")

# No additional code needed as gurobipy variables are non-negative by default unless explicitly set to allow negative values.

# Set objective
model.setObjective(EscalatorSpace * NumberOfEscalators + ElevatorSpace * NumberOfElevators, gp.GRB.MINIMIZE)

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
