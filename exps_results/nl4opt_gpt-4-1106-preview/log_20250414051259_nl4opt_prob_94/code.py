import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_94/data.json", "r") as f:
    data = json.load(f)

InertGasA = data["InertGasA"] # scalar parameter
WaterA = data["WaterA"] # scalar parameter
CompoundA = data["CompoundA"] # scalar parameter
InertGasB = data["InertGasB"] # scalar parameter
WaterB = data["WaterB"] # scalar parameter
CompoundB = data["CompoundB"] # scalar parameter
TotalInertGas = data["TotalInertGas"] # scalar parameter
TotalWater = data["TotalWater"] # scalar parameter
NumberOfReactionA = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfReactionA")
NumberOfReactionB = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfReactionB")

# Since NumberOfReactionA is already a non-negative integer variable by virtue of its type, no additional constraint is needed.
# The Gurobi integer variable type enforces non-negativity by default.

# Since the variable NumberOfReactionB is already required to be integer (which includes non-negative values by default in Gurobi for integer variables), no separate constraint is needed to enforce non-negativity.

# Add constraint for total use of inert gas by reaction A and B
model.addConstr(InertGasA * NumberOfReactionA + InertGasB * NumberOfReactionB <= TotalInertGas, name="total_inert_gas_usage")

# Constraint: Total use of treated water for chemical reactions A and B does not exceed the total available water
model.addConstr(WaterA * NumberOfReactionA + WaterB * NumberOfReactionB <= TotalWater, "total_water_usage")

# Define the objective function
model.setObjective(CompoundA * NumberOfReactionA + CompoundB * NumberOfReactionB, gp.GRB.MAXIMIZE)

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
