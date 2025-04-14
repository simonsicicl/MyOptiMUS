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
NumberOfReactionsA = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfReactionsA")
NumberOfReactionsB = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfReactionsB")

# Ensure the number of chemical reactions A is non-negative
model.addConstr(NumberOfReactionsA >= 0, name="non_negative_reactions_A")

# The variable NumberOfReactionsB is already defined as non-negative because it is continuous by default in Gurobi (vtype=gp.GRB.CONTINUOUS).

# Add constraint to ensure the total use of inert gas by reactions does not exceed the total available inert gas
model.addConstr(InertGasA * NumberOfReactionsA + InertGasB * NumberOfReactionsB <= TotalInertGas, name="inert_gas_limit")

# Add constraint for total use of treated water
model.addConstr(WaterA * NumberOfReactionsA + WaterB * NumberOfReactionsB <= TotalWater, name="treated_water_limit")

# Add inert gas usage constraint for reactions A and B
model.addConstr((NumberOfReactionsA * InertGasA) + (NumberOfReactionsB * InertGasB) <= TotalInertGas, name="inert_gas_usage")

# Add treated water usage constraint
model.addConstr(
    (WaterA * NumberOfReactionsA) + (WaterB * NumberOfReactionsB) <= TotalWater,
    name="treated_water_usage"
)

# Ensure the number of reactions A is non-negative
model.addConstr(NumberOfReactionsA >= 0, name="non_negative_reactions_A")

# Ensure the number of reactions B is non-negative
model.addConstr(NumberOfReactionsB >= 0, name="non_negative_reactions_B")

# Set objective
model.setObjective((CompoundA * NumberOfReactionsA) + (CompoundB * NumberOfReactionsB), gp.GRB.MAXIMIZE)

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
