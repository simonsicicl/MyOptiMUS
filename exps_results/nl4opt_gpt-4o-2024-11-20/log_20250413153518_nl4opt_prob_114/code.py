import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_114/data.json", "r") as f:
    data = json.load(f)

FatApple = data["FatApple"] # scalar parameter
FolateApple = data["FolateApple"] # scalar parameter
FatCarrot = data["FatCarrot"] # scalar parameter
FolateCarrot = data["FolateCarrot"] # scalar parameter
MinServingsCarrot = data["MinServingsCarrot"] # scalar parameter
AppleCarrotRatio = data["AppleCarrotRatio"] # scalar parameter
MaxFolate = data["MaxFolate"] # scalar parameter
ServingsApple = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ServingsApple")
ServingsCarrot = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ServingsCarrot")

# The non-negativity of ServingsApple is already defined through its default lower bound of 0 in gurobipy. No additional constraint is required.

# No code needed, as non-negativity is inherent to the default behavior of Gurobi continuous variables.

# Add the constraint ensuring the ratio of apple to carrot servings
model.addConstr(ServingsApple == AppleCarrotRatio * ServingsCarrot, name="apple_carrot_ratio")

# Add constraint to ensure the baby eats at least the minimum required servings of carrot-flavored baby food
model.addConstr(ServingsCarrot >= MinServingsCarrot, name="min_servings_carrot")

# Add constraint to limit folate consumption
model.addConstr(ServingsApple * FolateApple + ServingsCarrot * FolateCarrot <= MaxFolate, name="folate_limit")

# Add constraint for minimum servings of carrot-flavored baby food
model.addConstr(ServingsCarrot >= MinServingsCarrot, name="min_servings_carrot")

# Add apple-to-carrot servings ratio constraint
model.addConstr(ServingsApple >= AppleCarrotRatio * ServingsCarrot, name="apple_carrot_ratio")

# Add folate intake constraint
model.addConstr(FolateApple * ServingsApple + FolateCarrot * ServingsCarrot <= MaxFolate, name="folate_intake_limit")

# Set objective
model.setObjective(FatApple * ServingsApple + FatCarrot * ServingsCarrot, gp.GRB.MAXIMIZE)

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
