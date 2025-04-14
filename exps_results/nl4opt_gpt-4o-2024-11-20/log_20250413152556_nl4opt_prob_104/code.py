import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_104/data.json", "r") as f:
    data = json.load(f)

VitaminDOrange = data["VitaminDOrange"] # scalar parameter
VitaminCOrange = data["VitaminCOrange"] # scalar parameter
VitaminDApple = data["VitaminDApple"] # scalar parameter
VitaminCApple = data["VitaminCApple"] # scalar parameter
MinRatioAppleToOrange = data["MinRatioAppleToOrange"] # scalar parameter
MinOrange = data["MinOrange"] # scalar parameter
MaxVitaminC = data["MaxVitaminC"] # scalar parameter
OrangeJuiceBoxes = model.addVar(vtype=gp.GRB.CONTINUOUS, name="OrangeJuiceBoxes")
AppleJuiceBoxes = model.addVar(vtype=gp.GRB.CONTINUOUS, name="AppleJuiceBoxes")

# Add constraint to ensure the number of orange juice boxes is non-negative
model.addConstr(OrangeJuiceBoxes >= 0, name="non_negative_orange_juice_boxes")

# The constraint is already satisfied as the variable AppleJuiceBoxes is defined with a lower bound of 0.

# Add constraint to ensure the number of apple juice boxes is at least MinRatioAppleToOrange times the number of orange juice boxes
model.addConstr(AppleJuiceBoxes >= MinRatioAppleToOrange * OrangeJuiceBoxes, name="apple_orange_ratio")

# Add minimum consumption constraint for orange juice boxes
model.addConstr(OrangeJuiceBoxes >= MinOrange, name="min_orange_consumption")

# Add vitamin C consumption constraint
model.addConstr(
    OrangeJuiceBoxes * VitaminCOrange + AppleJuiceBoxes * VitaminCApple <= MaxVitaminC,
    name="vitamin_c_constraint"
)

# Add constraint to ensure the number of apple juice boxes is at least MinRatioAppleToOrange times the number of orange juice boxes
model.addConstr(AppleJuiceBoxes >= MinRatioAppleToOrange * OrangeJuiceBoxes, name="min_ratio_apple_to_orange")

# Add constraint to ensure the minimum consumption of orange juice boxes
model.addConstr(OrangeJuiceBoxes >= MinOrange, name="min_orange_constraint")

# Add vitamin C intake constraint
model.addConstr(
    VitaminCOrange * OrangeJuiceBoxes + VitaminCApple * AppleJuiceBoxes <= MaxVitaminC,
    name="vitamin_c_intake"
)

# Set objective
model.setObjective(VitaminDOrange * OrangeJuiceBoxes + VitaminDApple * AppleJuiceBoxes, gp.GRB.MAXIMIZE)

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
