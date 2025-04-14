import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_208/data.json", "r") as f:
    data = json.load(f)

CaA = data["CaA"] # scalar parameter
MgA = data["MgA"] # scalar parameter
CaB = data["CaB"] # scalar parameter
MgB = data["MgB"] # scalar parameter
CostA = data["CostA"] # scalar parameter
CostB = data["CostB"] # scalar parameter
MinCa = data["MinCa"] # scalar parameter
MinMg = data["MinMg"] # scalar parameter
xA = model.addVar(vtype=gp.GRB.CONTINUOUS, name="xA")
xB = model.addVar(vtype=gp.GRB.CONTINUOUS, name="xB")

# The number of servings of health supplement A is already non-negative through the variable definition
# No need to add an extra constraint.

# Add non-negativity constraint for the servings of health supplement B
model.addConstr(xB >= 0, name="health_supplement_B_nonnegativity")

# Add constraint for minimum calcium requirement
model.addConstr(CaA * xA + CaB * xB >= MinCa, name="min_calcium_requirement")

# Constraint: Total Magnesium from servings of A and B must be at least MinMg grams
model.addConstr(MgA * xA + MgB * xB >= MinMg, name="min_magnesium_requirement")

# Ensure that the total amount of Calcium consumed per day meets or exceeds the minimum requirement
model.addConstr(CaA * xA + CaB * xB >= MinCa, name="calcium_requirement")

# Constraint for minimum Magnesium requirement
model.addConstr(MgA * xA + MgB * xB >= MinMg, name="min_magnesium")

# Set objective function
model.setObjective(CostA * xA + CostB * xB, gp.GRB.MINIMIZE)

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
