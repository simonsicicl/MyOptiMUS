import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_20/data.json", "r") as f:
    data = json.load(f)

ApplesStock = data["ApplesStock"] # scalar parameter
BananasStock = data["BananasStock"] # scalar parameter
GrapesStock = data["GrapesStock"] # scalar parameter
ApplesBHPack = data["ApplesBHPack"] # scalar parameter
GrapesBHPack = data["GrapesBHPack"] # scalar parameter
ProfitBHPack = data["ProfitBHPack"] # scalar parameter
ApplesCombo = data["ApplesCombo"] # scalar parameter
BananasCombo = data["BananasCombo"] # scalar parameter
GrapesCombo = data["GrapesCombo"] # scalar parameter
ProfitCombo = data["ProfitCombo"] # scalar parameter
BananaHaterPackages = model.addVar(vtype=gp.GRB.CONTINUOUS, name="BananaHaterPackages")
ComboPackages = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ComboPackages")

# No code needed, as non-negativity is inherent to the default lower bound of Gurobi continuous variables,
# i.e., variables are >= 0 by default.

# The variable ComboPackages already has a non-negativity constraint due to being continuous, no additional code needed.

# Add constraint for total number of apples used in banana-haters and combo packages
model.addConstr(ApplesBHPack * BananaHaterPackages + ApplesCombo * ComboPackages <= ApplesStock, 
                name="apple_stock_constraint")

# Adding the constraint for banana combos and stock
model.addConstr(ComboPackages * BananasCombo <= BananasStock, 
                name="bananas_stock_constraint")

# Add grape stock constraint
model.addConstr(
    BananaHaterPackages * GrapesBHPack + ComboPackages * GrapesCombo <= GrapesStock,
    name="grape_stock_limit"
)

# Add constraint to ensure apple usage does not exceed the stock
model.addConstr(
    ApplesBHPack * BananaHaterPackages + ApplesCombo * ComboPackages <= ApplesStock,
    name="apple_stock_limit"
)

# Add constraint to ensure the total bananas used do not exceed the stock
model.addConstr(ComboPackages * BananasCombo <= BananasStock, name="bananas_stock_constraint")

# Add constraint: total number of grapes used cannot exceed the stock of grapes
model.addConstr(
    GrapesBHPack * BananaHaterPackages + GrapesCombo * ComboPackages <= GrapesStock, 
    name="grapes_stock_limit"
)

# Set objective
model.setObjective(ProfitBHPack * BananaHaterPackages + ProfitCombo * ComboPackages, gp.GRB.MAXIMIZE)

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
