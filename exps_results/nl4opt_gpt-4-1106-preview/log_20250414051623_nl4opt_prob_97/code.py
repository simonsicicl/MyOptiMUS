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
NumberOfPremiumPrinters = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfPremiumPrinters")
NumberOfRegularPrinters = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfRegularPrinters")

# Add non-negativity constraint for the number of premium printers
model.addConstr(NumberOfPremiumPrinters >= 0, name="premium_printers_nonnegativity")

# Constraint to ensure the number of regular printers is non-negative
model.addConstr(NumberOfRegularPrinters >= 0, name="non_negative_regular_printers")

# Add minimum total printing speed constraint
model.addConstr((NumberOfPremiumPrinters * PremiumSpeed) + (NumberOfRegularPrinters * RegularSpeed) >= MinPages, name="min_printing_speed")

# Add constraint for the total ink usage not to exceed MaxInk
ink_usage = NumberOfPremiumPrinters * PremiumInkUse + NumberOfRegularPrinters * RegularInkUse
model.addConstr(ink_usage <= MaxInk, name="total_ink_usage")

# Ensure that the minimum pages required by the office are printed per minute
model.addConstr(NumberOfPremiumPrinters * PremiumSpeed + NumberOfRegularPrinters * RegularSpeed >= MinPages, 
                name="MinPagesConstraint")

# Ensure that the maximum units of ink used per minute by the office are not exceeded
model.addConstr(NumberOfPremiumPrinters * PremiumInkUse + NumberOfRegularPrinters * RegularInkUse <= MaxInk, name="max_ink_usage")

# Set objective
model.setObjective(NumberOfPremiumPrinters + NumberOfRegularPrinters, gp.GRB.MINIMIZE)

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
