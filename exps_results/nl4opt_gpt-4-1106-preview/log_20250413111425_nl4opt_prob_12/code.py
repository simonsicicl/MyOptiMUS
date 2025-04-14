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
NumRegSandwiches = model.addVar(vtype=gp.GRB.INTEGER, name="NumRegSandwiches")
NumSpecSandwiches = model.addVar(vtype=gp.GRB.INTEGER, name="NumSpecSandwiches")

# No additional code is needed because the variable NumRegSandwiches is already defined as an integer in the provided code.

# Since NumSpecSandwiches is already defined as an integer variable, no additional constraint is required for integrality.

# Add constraint for non-negative number of regular sandwiches
model.addConstr(NumRegSandwiches >= 0, name="non_negativity_NumRegSandwiches")

model.addConstr(NumSpecSandwiches >= 0, name="non_negativity_special_sandwiches")

# Ensure that total eggs used in making sandwiches do not exceed the available eggs
model.addConstr(EggsReg * NumRegSandwiches + EggsSpec * NumSpecSandwiches <= TotalEggs, name="egg_availability_constraint")

# Bacon constraint: total bacon used for all sandwiches cannot exceed total available bacon
model.addConstr(BaconReg * NumRegSandwiches + BaconSpec * NumSpecSandwiches <= TotalBacon, "bacon_limit")

# Egg usage constraint: The number of eggs used must not exceed the total number of eggs available
model.addConstr(
    EggsReg * NumRegSandwiches + EggsSpec * NumSpecSandwiches <= TotalEggs, 
    name="egg_usage_constraint"
)

# Constraint for the total number of bacon slices used
model.addConstr(BaconReg * NumRegSandwiches + BaconSpec * NumSpecSandwiches <= TotalBacon, name="bacon_availability")

# Set objective function
model.setObjective(ProfitReg * NumRegSandwiches + ProfitSpec * NumSpecSandwiches, gp.GRB.MAXIMIZE)

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
