import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_3/data.json", "r") as f:
    data = json.load(f)

TotalAcres = data["TotalAcres"] # scalar parameter
MinApples = data["MinApples"] # scalar parameter
MinPears = data["MinPears"] # scalar parameter
ProfitApple = data["ProfitApple"] # scalar parameter
ProfitPear = data["ProfitPear"] # scalar parameter
MaxPearsToApplesRatio = data["MaxPearsToApplesRatio"] # scalar parameter
AppleAcres = model.addVar(vtype=gp.GRB.CONTINUOUS, name="AppleAcres")
PearAcres = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PearAcres")

# Change the variable "AppleAcres" type to integer to ensure it is an integer value
AppleAcres.vtype = gp.GRB.INTEGER

# Update variable type to integer since PearAcres must be an integer
PearAcres.vtype = gp.GRB.INTEGER

# No code is needed: Gurobi variables by default have non-negativity constraints unless otherwise specified (e.g., if set to unrestricted).

# No additional code needed since the non-negativity is enforced by default due to the variable's lower bound being 0.

# Add constraint ensuring the number of acres allocated for apples meets the minimum requirement
model.addConstr(AppleAcres >= MinApples, name="min_apples_acres")

# Add constraint ensuring the minimum acres allocated for growing pears
model.addConstr(PearAcres >= MinPears, name="min_pear_acres")

# Add constraint: PearAcres <= MaxPearsToApplesRatio * AppleAcres
model.addConstr(PearAcres <= MaxPearsToApplesRatio * AppleAcres, name="pear_to_apple_ratio")

# Add constraint to ensure total apple and pear acres do not exceed total available acres
model.addConstr(AppleAcres + PearAcres <= TotalAcres, name="acres_constraint")

# Add constraint to ensure total land allocated to apples and pears does not exceed total available acres
model.addConstr(AppleAcres + PearAcres <= TotalAcres, name="land_allocation_constraint")

# Add minimum acreage constraint for apples
model.addConstr(AppleAcres >= MinApples, name="min_apples_acreage")

# Add minimum acreage constraint for pears
model.addConstr(PearAcres >= MinPears, name="min_pears_acreage")

# Add constraint to ensure the ratio of PearAcres to AppleAcres does not exceed MaxPearsToApplesRatio
model.addConstr(PearAcres <= MaxPearsToApplesRatio * AppleAcres, name="pear_to_apple_ratio")

# Set objective
model.setObjective(ProfitApple * AppleAcres + ProfitPear * PearAcres, gp.GRB.MAXIMIZE)

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
