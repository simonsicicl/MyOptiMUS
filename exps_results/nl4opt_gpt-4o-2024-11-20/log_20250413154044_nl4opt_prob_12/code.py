import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_12/data.json", "r") as f:
    data = json.load(f)

EggsReg = data["EggsReg"] # scalar parameter
EggsSpec = data["EggsSpec"] # scalar parameter
BaconReg = data["BaconReg"] # scalar parameter
BaconSpec = data["BaconSpec"] # scalar parameter
TotalEggs = data["TotalEggs"] # scalar parameter
TotalBacon = data["TotalBacon"] # scalar parameter
ProfitReg = data["ProfitReg"] # scalar parameter
ProfitSpec = data["ProfitSpec"] # scalar parameter
RegularSandwiches = model.addVar(vtype=gp.GRB.CONTINUOUS, name="RegularSandwiches")
SpecialSandwiches = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SpecialSandwiches")

# Changing RegularSandwiches to be an integer variable
RegularSandwiches.vtype = gp.GRB.INTEGER

# Changing the integrality of the variable 'SpecialSandwiches' to integer
SpecialSandwiches.vtype = gp.GRB.INTEGER

# The RegularSandwiches variable is already coded with a non-negative domain due to its default non-negative domain in Gurobi,
# so no constraint code is needed.

# No additional code needed since the variable "SpecialSandwiches" is already defined as non-negative (its default lower bound is 0)

# Adding constraint to ensure total eggs used does not exceed available eggs
model.addConstr(
    RegularSandwiches * EggsReg + SpecialSandwiches * EggsSpec <= TotalEggs,
    name="egg_constraint"
)

# Add bacon usage constraint
model.addConstr(
    BaconReg * RegularSandwiches + BaconSpec * SpecialSandwiches <= TotalBacon,
    name="bacon_usage_limit"
)

# Add eggs availability constraint
model.addConstr(EggsReg * RegularSandwiches + EggsSpec * SpecialSandwiches <= TotalEggs, name="eggs_availability")

# Adding the bacon availability constraint
model.addConstr(
    RegularSandwiches * BaconReg + SpecialSandwiches * BaconSpec <= TotalBacon,
    name="bacon_availability"
)

# Add non-negativity constraint for RegularSandwiches
model.addConstr(RegularSandwiches >= 0, name="non_negativity_RegularSandwiches")

# Add non-negativity constraint for SpecialSandwiches
model.addConstr(SpecialSandwiches >= 0, name="non_negativity_SpecialSandwiches")

# Set objective
model.setObjective(ProfitReg * RegularSandwiches + ProfitSpec * SpecialSandwiches, gp.GRB.MAXIMIZE)

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
