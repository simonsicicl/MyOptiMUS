import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_89/data.json", "r") as f:
    data = json.load(f)

GoatMeatPerGoatCurry = data["GoatMeatPerGoatCurry"] # scalar parameter
CurryBasePerGoatCurry = data["CurryBasePerGoatCurry"] # scalar parameter
ChickenMeatPerChickenCurry = data["ChickenMeatPerChickenCurry"] # scalar parameter
CurryBasePerChickenCurry = data["CurryBasePerChickenCurry"] # scalar parameter
TotalGoatMeat = data["TotalGoatMeat"] # scalar parameter
TotalChickenMeat = data["TotalChickenMeat"] # scalar parameter
MinChickenCurryProportion = data["MinChickenCurryProportion"] # scalar parameter
GoatCurryBowls = model.addVar(vtype=gp.GRB.CONTINUOUS, name="GoatCurryBowls")
ChickenCurryBowls = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ChickenCurryBowls")

# Add constraint for non-negativity of the number of goat curry bowls
model.addConstr(GoatCurryBowls >= 0, name="GoatCurryBowls_nonnegativity")

model.addConstr(ChickenCurryBowls >= 0, name="non_negativity_chicken_curry_bowls")

# Constraint: Total goat meat used in goat curry bowls must not exceed available units of goat meat
model.addConstr(GoatMeatPerGoatCurry * GoatCurryBowls <= TotalGoatMeat, name="GoatMeatUsage")

# Chicken meat availability constraint
ChickenCurryBowls = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ChickenCurryBowls") # If not previously defined
model.addConstr(ChickenMeatPerChickenCurry * ChickenCurryBowls <= TotalChickenMeat, name="chicken_meat_availability")

# Add constraint: At least a certain proportion of the total bowls produced should be chicken curry
model.addConstr(ChickenCurryBowls >= MinChickenCurryProportion * (GoatCurryBowls + ChickenCurryBowls), "MinChickenCurryProportionConstraint")

# Add constraint that goat curry bowls must be greater than or equal to chicken curry bowls plus one
model.addConstr(GoatCurryBowls - ChickenCurryBowls >= 1, name="goat_chicken_curry_bowls_constraint")

# Set objective function
model.setObjective(CurryBasePerGoatCurry * GoatCurryBowls + CurryBasePerChickenCurry * ChickenCurryBowls, gp.GRB.MINIMIZE)

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
