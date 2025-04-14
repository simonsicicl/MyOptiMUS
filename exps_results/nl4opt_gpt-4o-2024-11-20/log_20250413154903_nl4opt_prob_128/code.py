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
LiquidSanitizers = model.addVar(vtype=gp.GRB.CONTINUOUS, name="LiquidSanitizers")
FoamSanitizers = model.addVar(vtype=gp.GRB.CONTINUOUS, name="FoamSanitizers")

# Add constraint to ensure the number of liquid hand sanitizers is non-negative
model.addConstr(LiquidSanitizers >= 0, name="non_negative_liquid_sanitizers")

# No code is needed as the non-negativity is defined inherently by the lower bound of the FoamSanitizers variable during its creation (default lb=0).

# Add water usage constraint
model.addConstr(
    LiquidSanitizers * WaterL + FoamSanitizers * WaterF <= WaterTotal, 
    name="water_usage_constraint"
)

# Add constraint for total alcohol usage
model.addConstr(AlcoholL * LiquidSanitizers + AlcoholF * FoamSanitizers <= AlcoholTotal, name="alcohol_usage_limit")

# Add constraint to ensure FoamSanitizers exceed LiquidSanitizers by at least 1
model.addConstr(FoamSanitizers >= LiquidSanitizers + 1, name="foam_vs_liquid_sanitizers")

# Add constraint for limiting the maximum number of liquid hand sanitizers
model.addConstr(LiquidSanitizers <= MaxLiquid, name="max_liquid_sanitizers")

# Add water usage constraint
model.addConstr(WaterL * LiquidSanitizers + WaterF * FoamSanitizers <= WaterTotal, name="water_usage")

# Add alcohol usage constraint
model.addConstr(AlcoholL * LiquidSanitizers + AlcoholF * FoamSanitizers <= AlcoholTotal, name="alcohol_usage_constraint")

# Add production constraint for limiting liquid sanitizers
model.addConstr(LiquidSanitizers <= MaxLiquid, name="production_constraint")

# Add non-negativity constraints for production quantities
model.addConstr(LiquidSanitizers >= 0, name="non_negativity_LiquidSanitizers")
model.addConstr(FoamSanitizers >= 0, name="non_negativity_FoamSanitizers")

# Set objective
model.setObjective(CleanHandsL * LiquidSanitizers + CleanHandsF * FoamSanitizers, gp.GRB.MAXIMIZE)

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
