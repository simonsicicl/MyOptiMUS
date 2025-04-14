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

# Since the variable "FullWeightedKeyboards" is already defined as non-negative (default lower bound is 0 for continuous variables in Gurobi), no additional constraint is needed.

# Add constraint to ensure the number of semi-weighted keyboards is non-negative
model.addConstr(SemiWeightedKeyboards >= 0, name="SemiWeightedKeyboards_nonnegative")

# Add constraint for the total number of oscillator chips used
model.addConstr(
    ChipsFullWeighted * FullWeightedKeyboards + ChipsSemiWeighted * SemiWeightedKeyboards <= TotalChips,
    name="osillator_chips_limit"
)

# Add total production time constraint
model.addConstr(
    FullWeightedKeyboards * ProductionTimePerKeyboard +
    SemiWeightedKeyboards * ProductionTimePerKeyboard <= TotalTime,
    name="total_production_time"
)

# Add oscillator chip availability constraint
model.addConstr(
    ChipsFullWeighted * FullWeightedKeyboards + ChipsSemiWeighted * SemiWeightedKeyboards <= TotalChips,
    name="oscillator_chip_availability"
)

# Add constraint ensuring total production time does not exceed daily availability  
model.addConstr(  
    ProductionTimePerKeyboard * (FullWeightedKeyboards + SemiWeightedKeyboards) <= TotalTime,  
    name="production_time_constraint"  
)

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
