import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_1/data.json", "r") as f:
    data = json.load(f)

MaxColor = data["MaxColor"] # scalar parameter
MaxBW = data["MaxBW"] # scalar parameter
MaxTotal = data["MaxTotal"] # scalar parameter
ProfitColor = data["ProfitColor"] # scalar parameter
ProfitBW = data["ProfitBW"] # scalar parameter
ColorPrinters = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ColorPrinters")
BWPrinters = model.addVar(vtype=gp.GRB.CONTINUOUS, name="BWPrinters")

# Changing the integrality of the variable to ensure it is an integer
ColorPrinters.vtype = gp.GRB.INTEGER

# Update BWPrinters variable integrality and add production capacity constraints
BWPrinters.vtype = gp.GRB.INTEGER  # Ensuring BWPrinters is an integer
model.addConstr(ColorPrinters + BWPrinters <= MaxTotal, name="total_printer_limit")
model.addConstr(ColorPrinters <= MaxColor, name="max_color_limit")
model.addConstr(BWPrinters <= MaxBW, name="max_bw_limit")

# The variable "ColorPrinters" already has non-negativity enforced internally due to its default non-negative domain in Gurobi,
# so no additional constraint code is required.

# The non-negativity of BWPrinters is already defined through its default lower bound of 0 in gurobipy

# Add constraint to limit the number of color printers produced per day
model.addConstr(ColorPrinters <= MaxColor, name="max_color_printers")

# Add constraint for the maximum number of black and white printers produced per day
model.addConstr(BWPrinters <= MaxBW, name="max_BW_printers")

# Add printer production capacity constraint
model.addConstr(ColorPrinters + BWPrinters <= MaxTotal, name="printer_capacity")

# Add constraint to limit ColorPrinters to the maximum allowable production
model.addConstr(ColorPrinters <= MaxColor, name="max_color_printers")

# Add a constraint to ensure the number of black and white printers produced per day does not exceed MaxBW
model.addConstr(BWPrinters <= MaxBW, name="max_bw_printers")

# Add constraint to ensure total printers do not exceed machine capacity
model.addConstr(ColorPrinters + BWPrinters <= MaxTotal, name="total_printer_capacity")

# Set objective
model.setObjective(
    ProfitColor * ColorPrinters + ProfitBW * BWPrinters,
    gp.GRB.MAXIMIZE
)

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
