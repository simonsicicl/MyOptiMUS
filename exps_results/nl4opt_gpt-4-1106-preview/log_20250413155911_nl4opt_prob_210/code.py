import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_210/data.json", "r") as f:
    data = json.load(f)

RevenueLight = data["RevenueLight"] # scalar parameter
RevenueNonSticky = data["RevenueNonSticky"] # scalar parameter
RevenueHeavy = data["RevenueHeavy"] # scalar parameter
CompoundALight = data["CompoundALight"] # scalar parameter
CompoundBLight = data["CompoundBLight"] # scalar parameter
CompoundANonSticky = data["CompoundANonSticky"] # scalar parameter
CompoundBNonSticky = data["CompoundBNonSticky"] # scalar parameter
CompoundAHeavy = data["CompoundAHeavy"] # scalar parameter
CompoundBHeavy = data["CompoundBHeavy"] # scalar parameter
TotalCompoundA = data["TotalCompoundA"] # scalar parameter
TotalCompoundB = data["TotalCompoundB"] # scalar parameter
NumLightOilTanks = model.addVar(vtype=gp.GRB.INTEGER, name="NumLightOilTanks")
NumNonStickyOilTanks = model.addVar(vtype=gp.GRB.INTEGER, name="NumNonStickyOilTanks")
NumHeavyOilTanks = model.addVar(vtype=gp.GRB.INTEGER, name="NumHeavyOilTanks")

# No code needed as the variable is already defined to be non-negative by setting its type to INTEGER.
# The constraint "NumLightOilTanks >= 0" is implicitly handled by the variable type definition.

# Constraint: Number of non-sticky oil tanks processed must be non-negative
model.addConstr(NumNonStickyOilTanks >= 0, "non_negative_tanks")

# Constraint for non-negative number of heavy oil tanks processed
model.addConstr(NumHeavyOilTanks >= 0, name="non_negative_heavy_oil_tanks")

# Constraint: Consumption of compound A for light oil does not exceed TotalCompoundA
model.addConstr(NumLightOilTanks * CompoundALight <= TotalCompoundA, name="compound_A_consumption")

# Constraint: Consumption of compound B for light oil does not exceed TotalCompoundB
model.addConstr(NumLightOilTanks * CompoundBLight <= TotalCompoundB, name="B_consumption_light_oil")

# Total consumption of compound A for all oils does not exceed available compound A
model.addConstr(CompoundALight * NumLightOilTanks + CompoundANonSticky * NumNonStickyOilTanks + CompoundAHeavy * NumHeavyOilTanks <= TotalCompoundA, name="TotalCompoundA_Constraint")

# Total consumption of compound B for all oils does not exceed TotalCompoundB
model.addConstr(CompoundBLight * NumLightOilTanks + CompoundBNonSticky * NumNonStickyOilTanks + CompoundBHeavy * NumHeavyOilTanks <= TotalCompoundB, name="B_consumption_constraint")

# Objective function
model.setObjective(RevenueLight * NumLightOilTanks + RevenueNonSticky * NumNonStickyOilTanks + RevenueHeavy * NumHeavyOilTanks, gp.GRB.MAXIMIZE)

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
