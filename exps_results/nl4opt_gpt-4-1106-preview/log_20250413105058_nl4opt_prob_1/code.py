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
NumberOfColorPrinters = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfColorPrinters")
NumberOfBlackAndWhitePrinters = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfBlackAndWhitePrinters")

# Since the variable NumberOfColorPrinters is already defined as an integer variable, no additional constraint is required for integrality.

# Constraint to ensure color printers do not exceed their maximum
model.addConstr(NumberOfColorPrinters <= MaxColor, name="MaxColorPrintersConstraint")

# Constraint to ensure black and white printers do not exceed their maximum
model.addConstr(NumberOfBlackAndWhitePrinters <= MaxBW, name="MaxBWPrintersConstraint")

# Constraint to ensure the total number of printers does not exceed the combined maximum
model.addConstr(NumberOfColorPrinters + NumberOfBlackAndWhitePrinters <= MaxTotal, name="MaxTotalPrintersConstraint")

# Since NumberOfColorPrinters is already defined as a variable, we only need to add the non-negativity constraint
model.addConstr(NumberOfColorPrinters >= 0, name="non_negativity_color_printers")

# Since NumberOfBlackAndWhitePrinters is already declared as an integer variable, we just need to add the non-negativity constraint
model.addConstr(NumberOfBlackAndWhitePrinters >= 0, "NonNegativityConstraint")

model.addConstr(NumberOfColorPrinters <= MaxColor, name="max_color_printers_constraint")

# Add constraint for maximum number of black and white printers produced per day
model.addConstr(NumberOfBlackAndWhitePrinters <= MaxBW, "max_black_white_printers")

# Total number of printers produced per day must not exceed the maximum capacity
model.addConstr(NumberOfColorPrinters + NumberOfBlackAndWhitePrinters <= MaxTotal, "capacity_constraint")

# Constraint: Number of color printers produced per day cannot exceed the maximum production capacity for color printers
model.addConstr(NumberOfColorPrinters <= MaxColor, name="max_color_printer_capacity")

NumberOfBlackAndWhitePrinters = model.addVar(vtype=gp.GRB.INTEGER, name='NumberOfBlackAndWhitePrinters')

# Total number of printers equipped with paper trays per day constraint
model.addConstr(NumberOfColorPrinters + NumberOfBlackAndWhitePrinters <= MaxTotal, name="capacity_constraint")

# Define the objective function
model.setObjective(ProfitColor * NumberOfColorPrinters + ProfitBW * NumberOfBlackAndWhitePrinters, gp.GRB.MAXIMIZE)

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
