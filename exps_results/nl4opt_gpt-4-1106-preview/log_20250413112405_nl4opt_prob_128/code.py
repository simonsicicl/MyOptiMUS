import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_128/data.json", "r") as f:
    data = json.load(f)

WaterL = data["WaterL"] # scalar parameter
AlcoholL = data["AlcoholL"] # scalar parameter
WaterF = data["WaterF"] # scalar parameter
AlcoholF = data["AlcoholF"] # scalar parameter
WaterTotal = data["WaterTotal"] # scalar parameter
AlcoholTotal = data["AlcoholTotal"] # scalar parameter
MaxLiquid = data["MaxLiquid"] # scalar parameter
CleanHandsL = data["CleanHandsL"] # scalar parameter
CleanHandsF = data["CleanHandsF"] # scalar parameter
LiquidSanitizersProduced = model.addVar(vtype=gp.GRB.INTEGER, name="LiquidSanitizersProduced")
FoamSanitizersProduced = model.addVar(vtype=gp.GRB.INTEGER, name="FoamSanitizersProduced")

# Since LiquidSanitizersProduced is already a non-negative integer variable, no additional constraint is needed.

# Non-negativity constraint for foam hand sanitizers production
model.addConstr(FoamSanitizersProduced >= 0, name="non_negative_FoamSanitizersProduced")

# Constraint for the total water used in producing liquid hand sanitizers
model.addConstr(WaterL * LiquidSanitizersProduced <= WaterTotal, name="water_usage_limit")

# Add constraint for total alcohol usage in producing liquid and foam hand sanitizers
model.addConstr(AlcoholL * LiquidSanitizersProduced + AlcoholF * FoamSanitizersProduced <= AlcoholTotal, name="alcohol_usage_constraint")

# Ensure foam hand sanitizers produced exceed liquid hand sanitizers by at least 1
model.addConstr(FoamSanitizersProduced >= LiquidSanitizersProduced + 1, 
                name="foam_exceeds_liquid")

# Ensure production doesn't exceed maximum capacity
model.addConstr(LiquidSanitizersProduced <= MaxLiquid, name="max_liquid_capacity_constraint")

# Set objective
model.setObjective(LiquidSanitizersProduced * CleanHandsL + FoamSanitizersProduced * CleanHandsF, gp.GRB.MAXIMIZE)

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
