import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_137/data.json", "r") as f:
    data = json.load(f)

VitaminCOrange = data["VitaminCOrange"] # scalar parameter
VitaminAOrange = data["VitaminAOrange"] # scalar parameter
SugarOrange = data["SugarOrange"] # scalar parameter
VitaminCGrapefruit = data["VitaminCGrapefruit"] # scalar parameter
VitaminAGrapefruit = data["VitaminAGrapefruit"] # scalar parameter
SugarGrapefruit = data["SugarGrapefruit"] # scalar parameter
MinVitaminC = data["MinVitaminC"] # scalar parameter
MinVitaminA = data["MinVitaminA"] # scalar parameter
OrangeGrapefruitRatio = data["OrangeGrapefruitRatio"] # scalar parameter
NumberOfOranges = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfOranges")
NumberOfGrapefruits = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfGrapefruits")

model.addConstr(NumberOfOranges >= 0, name="non_negativity_oranges")

# Add constraint to ensure the number of grapefruits is non-negative
model.addConstr(NumberOfGrapefruits >= 0, name="grapefruits_non_negative")

# Add constraint for the minimum total vitamin C from oranges and grapefruits
model.addConstr(VitaminCOrange * NumberOfOranges + VitaminCGrapefruit * NumberOfGrapefruits >= MinVitaminC, name="min_vitamin_c")

# Add constraint for the minimum total vitamin A from oranges and grapefruits
model.addConstr(NumberOfOranges * VitaminAOrange + NumberOfGrapefruits * VitaminAGrapefruit >= MinVitaminA, name="MinVitaminARequirement")

# Constraint for minimum oranges to grapefruits ratio
model.addConstr(NumberOfOranges >= OrangeGrapefruitRatio * NumberOfGrapefruits, name="min_oranges_to_grapefruits_ratio")

# Define Objective Function
model.setObjective(SugarOrange * NumberOfOranges + SugarGrapefruit * NumberOfGrapefruits, gp.GRB.MINIMIZE)

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
