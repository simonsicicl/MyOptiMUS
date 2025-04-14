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

model.addConstr(ServingsApple >= 0, name="ServingsApple_non_negative")

# Add constraint to ensure the servings of carrot flavored baby food is non-negative
model.addConstr(ServingsCarrot >= 0, name="ServingsCarrot_non_negative")

# Add the constraint that ServingsApple must be AppleCarrotRatio times ServingsCarrot
model.addConstr(ServingsApple == AppleCarrotRatio * ServingsCarrot, name="apple_to_carrot_ratio")

# Ensure baby eats at least the minimum servings of carrot flavored baby food
model.addConstr(ServingsCarrot >= MinServingsCarrot, "min_servings_carrot")

# Add constraint for maximum units of folate that the baby can consume
model.addConstr(ServingsApple * FolateApple + ServingsCarrot * FolateCarrot <= MaxFolate, 
                name="max_folate_intake")

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
