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
TotalBowls = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalBowls")

# Add non-negativity constraint for GoatCurryBowls
model.addConstr(GoatCurryBowls >= 0, name="non_negativity_GoatCurryBowls")

# No code needed, as non-negativity is inherent to the default lower bound of Gurobi continuous variables,
# i.e., variables are >= 0 by default.

# Add constraint to restrict total goat meat used in goat curry bowls
model.addConstr(GoatMeatPerGoatCurry * GoatCurryBowls <= TotalGoatMeat, name="goat_meat_limit")

# Add constraint: total chicken meat used must not exceed available chicken meat
model.addConstr(ChickenCurryBowls * ChickenMeatPerChickenCurry <= TotalChickenMeat, name="chicken_meat_limit")

# Add constraint for minimum proportion of chicken curry bowls
model.addConstr((1 - MinChickenCurryProportion) * ChickenCurryBowls >= MinChickenCurryProportion * GoatCurryBowls, 
                name="min_chicken_curry_proportion")

# Add constraint: The number of goat curry bowls must be greater than the number of chicken curry bowls
model.addConstr(GoatCurryBowls >= ChickenCurryBowls + 1, name="goat_vs_chicken_curry")

# Add constraint to ensure goat meat usage does not exceed availability
model.addConstr(GoatCurryBowls * GoatMeatPerGoatCurry <= TotalGoatMeat, name="goat_meat_usage")

# Add chicken meat usage constraint
model.addConstr(ChickenCurryBowls * ChickenMeatPerChickenCurry <= TotalChickenMeat, name="chicken_meat_usage")

# Add constraint: The proportion of chicken curry bowls must be at least the minimum specified proportion
model.addConstr(ChickenCurryBowls >= MinChickenCurryProportion * TotalBowls, name="min_chicken_curry_proportion")

# Add constraint to ensure TotalBowls equals the sum of GoatCurryBowls and ChickenCurryBowls
model.addConstr(TotalBowls == GoatCurryBowls + ChickenCurryBowls, name="total_bowls_constraint")

# Set objective
model.setObjective(GoatCurryBowls * CurryBasePerGoatCurry + ChickenCurryBowls * CurryBasePerChickenCurry, gp.GRB.MINIMIZE)

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
