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
NumberOfOranges = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfOranges")
NumberOfGrapefruits = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfGrapefruits")

# Non-negativity constraint for the number of oranges
model.addConstr(NumberOfOranges >= 0, name="non_negativity_NumberOfOranges")

# The constraint is already inherently satisfied by non-negative domain constraints of continuous variables,
# so no additional code is needed.

# Add vitamin C constraint from oranges and grapefruits
model.addConstr(
    VitaminCOrange * NumberOfOranges + VitaminCGrapefruit * NumberOfGrapefruits >= MinVitaminC,
    name="vitamin_C_requirement"
)

# Add constraint for minimum vitamin A intake
model.addConstr(VitaminAOrange * NumberOfOranges + VitaminAGrapefruit * NumberOfGrapefruits >= MinVitaminA, name="MinVitaminAConstraint")

# Add constraint that the number of oranges must be at least OrangeGrapefruitRatio times the number of grapefruits
model.addConstr(NumberOfOranges >= OrangeGrapefruitRatio * NumberOfGrapefruits, name="orange_grapefruit_ratio")

# Add Vitamin C intake constraint
model.addConstr(
    VitaminCOrange * NumberOfOranges + VitaminCGrapefruit * NumberOfGrapefruits >= MinVitaminC, 
    name="VitaminC_intake_constraint"
)

# Add Vitamin A intake constraint
model.addConstr(
    NumberOfOranges * VitaminAOrange + NumberOfGrapefruits * VitaminAGrapefruit >= MinVitaminA,
    name="vitaminA_requirement"
)

# Add constraint ensuring the specified ratio of oranges to grapefruits is maintained
model.addConstr(NumberOfOranges - OrangeGrapefruitRatio * NumberOfGrapefruits == 0, name="orange_grapefruit_ratio")

# Set objective
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
