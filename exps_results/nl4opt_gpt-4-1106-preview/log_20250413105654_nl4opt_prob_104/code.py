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
NumberOfOrangeJuiceBoxes = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfOrangeJuiceBoxes")
NumberOfAppleJuiceBoxes = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfAppleJuiceBoxes")

# Constraint: Number of orange juice boxes must be non-negative.
model.addConstr(NumberOfOrangeJuiceBoxes >= 0, name="non_negativity_OrangeJuiceBoxes")

# Since NumberOfAppleJuiceBoxes is already defined as an integer variable, 
# we just need to add a constraint to ensure it is non-negative.
model.addConstr(NumberOfAppleJuiceBoxes >= 0, "non_negativity_NumberOfAppleJuiceBoxes")

# Constraint: Number of apple juice boxes must be at least MinRatioAppleToOrange times the number of orange juice boxes
model.addConstr(NumberOfAppleJuiceBoxes >= MinRatioAppleToOrange * NumberOfOrangeJuiceBoxes, name="min_ratio_apple_to_orange")

MinOrange = data["MinOrange"]  # Assuming this comes from some data dictionary
# Add constraint: The scientist must drink at least MinOrange orange juice boxes
model.addConstr(NumberOfOrangeJuiceBoxes >= MinOrange, name="min_orange_juice_boxes")

# Add constraint for the maximum vitamin C intake from orange and apple juice boxes
model.addConstr(VitaminCOrange * NumberOfOrangeJuiceBoxes + VitaminCApple * NumberOfAppleJuiceBoxes <= MaxVitaminC, name="max_vitamin_C")

# Ensure the scientist drinks a minimum ratio of boxes of apple juice to orange juice
model.addConstr(NumberOfAppleJuiceBoxes >= MinRatioAppleToOrange * NumberOfOrangeJuiceBoxes, name="MinJuiceRatio")

# Ensure the scientist drinks at least the minimum number of orange juice boxes
model.addConstr(NumberOfOrangeJuiceBoxes >= MinOrange, name="min_orange_juice_boxes")

# Ensure the scientist does not exceed the maximum intake of vitamin C
model.addConstr(VitaminCApple * NumberOfAppleJuiceBoxes + VitaminCOrange * NumberOfOrangeJuiceBoxes <= MaxVitaminC, "Max_Vitamin_C_Intake")

# Set objective
model.setObjective(VitaminDApple * NumberOfAppleJuiceBoxes + VitaminDOrange * NumberOfOrangeJuiceBoxes, gp.GRB.MAXIMIZE)

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
