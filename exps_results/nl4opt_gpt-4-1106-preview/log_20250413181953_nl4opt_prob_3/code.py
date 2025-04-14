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
PearAcres = model.addVar(vtype=gp.GRB.INTEGER, name="PearAcres")

AppleAcres.vtype = gp.GRB.INTEGER

# Constraint: Total area for pears and apples cannot exceed available land
model.addConstr(AppleAcres + PearAcres <= TotalAcres, name="land_limit")

# Add non-negativity constraint for the number of apple acres
model.addConstr(AppleAcres >= 0, name="apple_acres_nonnegativity")

# Add non-negativity constraint for pear acres
model.addConstr(PearAcres >= 0, name="non_negativity_pear_acres")

# Add constraint for minimum apple acres
model.addConstr(AppleAcres >= MinApples, name="min_apple_acres")

# Constraint for the minimum required pear acres
model.addConstr(PearAcres >= MinPears, name="min_pear_acres_constraint")

# Constraint: The number of pear acres must not exceed the maximum ratio of pears to apples in growing
model.addConstr(PearAcres <= MaxPearsToApplesRatio * AppleAcres, name="PearToAppleRatioConstraint")

# Assuming there needs to be a constraint relating AppleAcres and PearAcres to TotalAcres
model.addConstr(AppleAcres + PearAcres <= TotalAcres, 'TotalLandUse')

# Add objective, constraints, or other necessary parts of the formulation here
# For example, setting an objective function:
# model.setObjective(<some_expression>, gp.GRB.MAXIMIZE)

# And adding constraints, if any:
# model.addConstr(<constraint_expression>, 'ConstraintName')

# In this example, replace <some_expression> and <constraint_expression> with actual code

# Add constraint for the total acres used for apples and pears not to exceed the total acres available
model.addConstr(AppleAcres + PearAcres <= TotalAcres, name="total_acres_constraint")

# Add constraint for the minimum required pear acres
model.addConstr(PearAcres >= MinPears, name="min_pear_acres")

model.addConstr(AppleAcres >= MinApples, name="min_apple_acres")

# Add constraint for the ratio of pears to apples not exceeding the maximum allowed
model.addConstr(PearAcres <= MaxPearsToApplesRatio * AppleAcres, name="MaxPearsToApplesRatioConstraint")

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
