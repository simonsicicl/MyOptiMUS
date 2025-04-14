import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_102/data.json", "r") as f:
    data = json.load(f)

FlourBeaker1 = data["FlourBeaker1"] # scalar parameter
LiquidBeaker1 = data["LiquidBeaker1"] # scalar parameter
SlimeBeaker1 = data["SlimeBeaker1"] # scalar parameter
WasteBeaker1 = data["WasteBeaker1"] # scalar parameter
FlourBeaker2 = data["FlourBeaker2"] # scalar parameter
LiquidBeaker2 = data["LiquidBeaker2"] # scalar parameter
SlimeBeaker2 = data["SlimeBeaker2"] # scalar parameter
WasteBeaker2 = data["WasteBeaker2"] # scalar parameter
TotalFlour = data["TotalFlour"] # scalar parameter
TotalLiquid = data["TotalLiquid"] # scalar parameter
MaxWaste = data["MaxWaste"] # scalar parameter
NumberBeaker1Used = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberBeaker1Used")
NumberBeaker2Used = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberBeaker2Used")

# The non-negativity constraint is inherently satisfied as the variable `NumberBeaker1Used` is continuous (Gurobi's CONTINUOUS type allows non-negative values by default).

# The non-negativity constraint is inherently satisfied as the variable `NumberBeaker2Used` is defined as continuous (non-negative by default), no extra constraint needs to be added.

# Add a constraint to ensure total flour used by Beaker 1 and Beaker 2 is within the available total flour
model.addConstr(NumberBeaker1Used * FlourBeaker1 + NumberBeaker2Used * FlourBeaker2 <= TotalFlour, name="Flour_Constraint")

# Add total liquid usage constraint
model.addConstr(
    6 * NumberBeaker1Used + 3 * NumberBeaker2Used <= TotalLiquid,
    name="total_liquid_constraint"
)

# Add waste production constraint
model.addConstr(WasteBeaker1 * NumberBeaker1Used + WasteBeaker2 * NumberBeaker2Used <= MaxWaste, name="waste_limit")

# Add constraint to ensure flour usage does not exceed the available total supply
model.addConstr(
    FlourBeaker1 * NumberBeaker1Used + FlourBeaker2 * NumberBeaker2Used <= TotalFlour,
    name="flour_usage_limit"
)

# Add constraint to ensure liquid usage does not exceed total supply
model.addConstr(LiquidBeaker1 * NumberBeaker1Used + LiquidBeaker2 * NumberBeaker2Used <= TotalLiquid, name="liquid_usage_limit")

# Adding constraint to ensure total waste does not exceed the maximum allowed waste.
model.addConstr(
    WasteBeaker1 * NumberBeaker1Used + WasteBeaker2 * NumberBeaker2Used <= MaxWaste,
    name="waste_limit"
)

# Set objective
model.setObjective(SlimeBeaker1 * NumberBeaker1Used + SlimeBeaker2 * NumberBeaker2Used, gp.GRB.MAXIMIZE)

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
