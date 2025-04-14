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
ServingsA = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ServingsA")
ServingsB = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ServingsB")

# No additional code needed since ServingsA is already defined as a non-negative continuous variable

# Add non-negativity constraint for ServingsB
model.addConstr(ServingsB >= 0, name="non_negativity_ServingsB")

# Add calcium intake constraint
model.addConstr(
    ServingsA * CaA + ServingsB * CaB >= MinCa, 
    name="calcium_requirement"
)

# Add Magnesium constraint
model.addConstr(MgA * ServingsA + MgB * ServingsB >= MinMg, name="magnesium_requirement")

# Add constraint to ensure the supplements meet the minimum daily Calcium requirement
model.addConstr(CaA * ServingsA + CaB * ServingsB >= MinCa, name="min_daily_calcium")

# Add Magnesium requirement constraint
model.addConstr(MgA * ServingsA + MgB * ServingsB >= MinMg, name="magnesium_requirement")

# Set objective
model.setObjective(CostA * ServingsA + CostB * ServingsB, gp.GRB.MINIMIZE)

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
