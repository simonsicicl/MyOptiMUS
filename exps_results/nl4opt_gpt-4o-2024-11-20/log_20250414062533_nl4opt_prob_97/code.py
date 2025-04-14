import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_97/data.json", "r") as f:
    data = json.load(f)

PremiumSpeed = data["PremiumSpeed"] # scalar parameter
RegularSpeed = data["RegularSpeed"] # scalar parameter
PremiumInkUse = data["PremiumInkUse"] # scalar parameter
RegularInkUse = data["RegularInkUse"] # scalar parameter
MinPages = data["MinPages"] # scalar parameter
MaxInk = data["MaxInk"] # scalar parameter
NumPremiumPrinters = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumPremiumPrinters")
NumRegularPrinters = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumRegularPrinters")

# Add constraint to ensure the number of premium printers is non-negative
model.addConstr(NumPremiumPrinters >= 0, name="non_negative_NumPremiumPrinters")

# No code is needed because the non-negativity constraint is automatically enforced due to the default non-negative domain of continuous variables in Gurobi.

# Add constraint ensuring total printing speed meets the minimum required
model.addConstr(
    NumPremiumPrinters * PremiumSpeed + NumRegularPrinters * RegularSpeed >= MinPages, 
    name="minimum_printing_speed"
)

# Add total ink usage constraint
model.addConstr(
    NumPremiumPrinters * PremiumInkUse + NumRegularPrinters * RegularInkUse <= MaxInk, 
    name="total_ink_usage_constraint"
)

# Add constraint to ensure the total pages printed per minute meets the minimum required
model.addConstr(NumPremiumPrinters * PremiumSpeed + NumRegularPrinters * RegularSpeed >= MinPages, name="min_pages_constraint")

# Ensure the total ink used per minute does not exceed the maximum allowed
model.addConstr(
    NumPremiumPrinters * PremiumInkUse + NumRegularPrinters * RegularInkUse <= MaxInk,
    name="MaxInkUsage"
)

# Set objective
model.setObjective(NumPremiumPrinters + NumRegularPrinters, gp.GRB.MINIMIZE)

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
