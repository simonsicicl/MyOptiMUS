import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_243/data.json", "r") as f:
    data = json.load(f)

WasteFoodOriginal = data["WasteFoodOriginal"] # scalar parameter
WasteWrapOriginal = data["WasteWrapOriginal"] # scalar parameter
TimeOriginal = data["TimeOriginal"] # scalar parameter
WasteFoodExperimental = data["WasteFoodExperimental"] # scalar parameter
WasteWrapExperimental = data["WasteWrapExperimental"] # scalar parameter
TimeExperimental = data["TimeExperimental"] # scalar parameter
MaxWrapWaste = data["MaxWrapWaste"] # scalar parameter
MaxFoodWaste = data["MaxFoodWaste"] # scalar parameter
OriginalMealCount = model.addVar(vtype=gp.GRB.CONTINUOUS, name="OriginalMealCount")
ExperimentalMealCount = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ExperimentalMealCount")

# No additional code needed since the variable "OriginalMealCount" is non-negative by default (continuous variables in Gurobi are non-negative unless otherwise specified).

# No additional code needed since the variable "ExperimentalMealCount" is already defined with non-negativity guaranteed by Gurobi's default behavior for continuous variables (lower bound is 0).

# Add food waste constraint
model.addConstr(
    (OriginalMealCount * WasteFoodOriginal) + (ExperimentalMealCount * WasteFoodExperimental) <= MaxFoodWaste,
    name="food_waste_limit"
)

# Add constraint to limit the wrapping waste
model.addConstr(OriginalMealCount * WasteWrapOriginal + ExperimentalMealCount * WasteWrapExperimental <= MaxWrapWaste, name="wrap_waste_limit")

# Add wrapping waste constraint
model.addConstr(
    OriginalMealCount * WasteWrapOriginal + ExperimentalMealCount * WasteWrapExperimental <= MaxWrapWaste,
    name="wrapping_waste_constraint"
)

# Add total food waste constraint
model.addConstr(
    WasteFoodOriginal * OriginalMealCount + WasteFoodExperimental * ExperimentalMealCount <= MaxFoodWaste,
    name="food_waste_constraint"
)

# Set objective
model.setObjective(TimeOriginal * OriginalMealCount + TimeExperimental * ExperimentalMealCount, gp.GRB.MINIMIZE)

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
