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
NumberOfOriginalMeals = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfOriginalMeals")
NumberOfExperimentalMeals = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfExperimentalMeals")

# Add constraint for non-negativity of original meals produced
model.addConstr(NumberOfOriginalMeals >= 0, name="nonnegativity_original_meals")

model.addConstr(NumberOfExperimentalMeals >= 0, "NumberOfExperimentalMeals_nonnegativity")

# Add constraint for total food waste from original and experimental meals not to exceed MaxFoodWaste
model.addConstr(WasteFoodOriginal * NumberOfOriginalMeals + WasteFoodExperimental * NumberOfExperimentalMeals <= MaxFoodWaste, name="food_waste_limit")

# Add constraint for total wrapping waste
model.addConstr(NumberOfOriginalMeals * WasteWrapOriginal + NumberOfExperimentalMeals * WasteWrapExperimental <= MaxWrapWaste, name="Max_Wrapping_Waste")

# Constraint: Maximum allowable wrapping waste units must not be exceeded
model.addConstr(WasteWrapOriginal * NumberOfOriginalMeals + WasteWrapExperimental * NumberOfExperimentalMeals <= MaxWrapWaste, "max_wrapping_waste_constraint")

# Add constraint for maximum allowable food waste units
model.addConstr(WasteFoodOriginal * NumberOfOriginalMeals + WasteFoodExperimental * NumberOfExperimentalMeals <= MaxFoodWaste, name="max_food_waste")

# Define the objective function
model.setObjective(TimeOriginal * NumberOfOriginalMeals + TimeExperimental * NumberOfExperimentalMeals, gp.GRB.MINIMIZE)

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
