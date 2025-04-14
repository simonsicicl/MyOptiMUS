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
NumberOfChopSaws = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfChopSaws")
NumberOfSteelCutters = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfSteelCutters")

# No additional code needed; non-negativity is enforced as the variable "NumberOfChopSaws" is defined as CONTINUOUS, which includes non-negative values by default in Gurobi.

# Add constraints for steel requirement and waste limit
model.addConstr(
    NumberOfChopSaws * PoundsChopSaw + NumberOfSteelCutters * PoundsSteelCutter >= TotalPounds,
    name="steel_requirement"
)
model.addConstr(
    NumberOfChopSaws * WasteChopSaw + NumberOfSteelCutters * WasteSteelCutter <= MaxWaste,
    name="waste_limit"
)

# Add daily production constraint for metal cutting
model.addConstr(
    PoundsChopSaw * NumberOfChopSaws + PoundsSteelCutter * NumberOfSteelCutters >= TotalPounds,
    name="daily_metal_cutting_requirement"
)

# Add waste production constraint
model.addConstr(NumberOfChopSaws * WasteChopSaw + NumberOfSteelCutters * WasteSteelCutter <= MaxWaste, name="waste_limit")

# No additional code needed since the variable 'NumberOfSteelCutters' is already defined as non-negative due to its default lower bound of 0 in Gurobi (gp.GRB.CONTINUOUS).

# No additional code needed as the non-negativity constraint is implicitly enforced by the default variable bounds (>= 0) when defining the continuous variable "NumberOfChopSaws" in Gurobipy.

# Add constraint to ensure the total pounds of steel worked meets the daily demand
model.addConstr(
    (PoundsChopSaw * NumberOfChopSaws) + (PoundsSteelCutter * NumberOfSteelCutters) >= TotalPounds, 
    name="total_pounds_constraint"
)

# Ensure total waste from chop saws and steel cutters does not exceed maximum allowed waste
model.addConstr(
    WasteChopSaw * NumberOfChopSaws + WasteSteelCutter * NumberOfSteelCutters <= MaxWaste, 
    name="waste_constraint"
)

# Set objective
model.setObjective(NumberOfChopSaws + NumberOfSteelCutters, gp.GRB.MINIMIZE)

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
