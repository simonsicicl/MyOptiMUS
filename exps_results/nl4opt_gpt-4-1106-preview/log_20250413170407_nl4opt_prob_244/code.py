import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_244/data.json", "r") as f:
    data = json.load(f)

PoundsChopSaw = data["PoundsChopSaw"] # scalar parameter
WasteChopSaw = data["WasteChopSaw"] # scalar parameter
PoundsSteelCutter = data["PoundsSteelCutter"] # scalar parameter
WasteSteelCutter = data["WasteSteelCutter"] # scalar parameter
TotalPounds = data["TotalPounds"] # scalar parameter
MaxWaste = data["MaxWaste"] # scalar parameter
NumChopSaws = model.addVar(vtype=gp.GRB.INTEGER, name="NumChopSaws")
NumSteelCutters = model.addVar(vtype=gp.GRB.INTEGER, name="NumSteelCutters")

# Add constraint to ensure the number of chop saws is non-negative
model.addConstr(NumChopSaws >= 0, name="NumChopSaws_non_negative")

# Add constraint to ensure the number of steel cutters is non-negative
model.addConstr(NumSteelCutters >= 0, "non_negativity_steel_cutters")

# Total pounds of metal cut daily constraint
model.addConstr(NumChopSaws * PoundsChopSaw + NumSteelCutters * PoundsSteelCutter >= TotalPounds, name="total_pounds_constraint")

# Add constraint for maximum daily waste
model.addConstr(WasteChopSaw * NumChopSaws + WasteSteelCutter * NumSteelCutters <= MaxWaste, name="max_daily_waste")

# Ensure that the total pounds of steel worked meets the daily demand
model.addConstr(NumChopSaws * PoundsChopSaw + NumSteelCutters * PoundsSteelCutter >= TotalPounds, "daily_demand")

# Add constraint for total waste not to exceed maximum allowed waste
model.addConstr(NumChopSaws * WasteChopSaw + NumSteelCutters * WasteSteelCutter <= MaxWaste, name="max_waste_constraint")

# Set objective
model.setObjective(NumChopSaws + NumSteelCutters, gp.GRB.MINIMIZE)

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
