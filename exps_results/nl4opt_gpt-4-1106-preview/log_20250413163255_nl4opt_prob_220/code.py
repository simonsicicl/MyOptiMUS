import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_220/data.json", "r") as f:
    data = json.load(f)

FullWeightedPrice = data["FullWeightedPrice"] # scalar parameter
SemiWeightedPrice = data["SemiWeightedPrice"] # scalar parameter
TotalChips = data["TotalChips"] # scalar parameter
ChipsFullWeighted = data["ChipsFullWeighted"] # scalar parameter
ChipsSemiWeighted = data["ChipsSemiWeighted"] # scalar parameter
TotalTime = data["TotalTime"] # scalar parameter
ProductionTimePerKeyboard = data["ProductionTimePerKeyboard"] # scalar parameter
FullWeightedKeyboards = model.addVar(vtype=gp.GRB.CONTINUOUS, name="FullWeightedKeyboards")
SemiWeightedKeyboards = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SemiWeightedKeyboards")

# Since FullWeightedKeyboards is already a non-negative continuous variable by default, no additional constraint is needed.

# Add constraint that the number of semi-weighted keyboards must be non-negative
model.addConstr(SemiWeightedKeyboards >= 0, name="non_negative_semiweighted_keyboards")

# Total number of chips used for full-weighted and semi-weighted keyboards cannot exceed total number of chips available
model.addConstr(ChipsFullWeighted * FullWeightedKeyboards + ChipsSemiWeighted * SemiWeightedKeyboards <= TotalChips, "chip_capacity_constraint")

# Add constraint for total production time of full-weighted and semi-weighted keyboards
model.addConstr(ProductionTimePerKeyboard * (FullWeightedKeyboards + SemiWeightedKeyboards) <= TotalTime, name="production_time_limit")

# Total oscillator chips used should not exceed the available number per day
model.addConstr(ChipsFullWeighted * FullWeightedKeyboards + ChipsSemiWeighted * SemiWeightedKeyboards <= TotalChips, "oscillator_chips_constraint")

# Add constraint to ensure the total production time does not exceed the total available time per day
model.addConstr(ProductionTimePerKeyboard * (FullWeightedKeyboards + SemiWeightedKeyboards) <= TotalTime, name="production_time")

# Set objective
model.setObjective(FullWeightedPrice * FullWeightedKeyboards + SemiWeightedPrice * SemiWeightedKeyboards, gp.GRB.MAXIMIZE)

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
