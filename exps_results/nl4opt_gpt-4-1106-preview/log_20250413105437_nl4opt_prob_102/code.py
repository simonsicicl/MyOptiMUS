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
NumberOfBeakersUsed1 = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfBeakersUsed1")
NumberOfBeakersUsed2 = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfBeakersUsed2")

# Add constraint to ensure the number of Beaker 1 used is non-negative
model.addConstr(NumberOfBeakersUsed1 >= 0, name="non_negativity_beaker1")

# Since NumberOfBeakersUsed2 is already defined as an integer variable, by default it is non-negative in Gurobi.
# No need to add an explicit constraint.

# Total flour used by Beaker 1 and Beaker 2 should not exceed TotalFlour
model.addConstr(NumberOfBeakersUsed1 * FlourBeaker1 + NumberOfBeakersUsed2 * FlourBeaker2 <= TotalFlour, "total_flour_constraint")

# Constraint: Total liquid used by Beaker 1 and Beaker 2 is less than or equal to TotalLiquid
model.addConstr(NumberOfBeakersUsed1 * LiquidBeaker1 + NumberOfBeakersUsed2 * LiquidBeaker2 <= TotalLiquid, name="TotalLiquidConstraint")

# Total waste produced by Beaker 1 and Beaker 2 should not exceed MaxWaste
model.addConstr(NumberOfBeakersUsed1 * WasteBeaker1 + NumberOfBeakersUsed2 * WasteBeaker2 <= MaxWaste, name="max_waste_constraint")

# The camp cannot use more flour than is available
model.addConstr(NumberOfBeakersUsed1 * FlourBeaker1 + NumberOfBeakersUsed2 * FlourBeaker2 <= TotalFlour, "flour_usage_constraint")

# Constraint: The camp cannot use more liquid than is available
model.addConstr(NumberOfBeakersUsed1 * LiquidBeaker1 + NumberOfBeakersUsed2 * LiquidBeaker2 <= TotalLiquid, "liquid_usage_limit")

# Add waste generation limit constraint
model.addConstr(
    NumberOfBeakersUsed1 * WasteBeaker1 + NumberOfBeakersUsed2 * WasteBeaker2 <= MaxWaste,
    name="waste_generation_limit"
)

# Define the objective function
model.setObjective(SlimeBeaker1 * NumberOfBeakersUsed1 + SlimeBeaker2 * NumberOfBeakersUsed2, gp.GRB.MAXIMIZE)

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
