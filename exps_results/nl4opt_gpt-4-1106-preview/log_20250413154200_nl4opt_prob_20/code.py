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
BananaHatersPackagesSold = model.addVar(vtype=gp.GRB.INTEGER, name="BananaHatersPackagesSold")
ComboPackagesSold = model.addVar(vtype=gp.GRB.INTEGER, name="ComboPackagesSold")

# Since BananaHatersPackagesSold is already declared as a non-negative integer variable, no additional constraints are needed.
# The non-negativity is handled by the variable type definition.

model.addConstr(ComboPackagesSold >= 0, name="non_negativity_constraint")

# Apple stock constraint
model.addConstr(BananaHatersPackagesSold * ApplesBHPack + ComboPackagesSold * ApplesCombo <= ApplesStock, name="apple_stock_constraint")

# Constraint: The total number of bananas used in combo packages must not exceed the stock of bananas available
BananasCombo = data["BananasCombo"] # scalar parameter
BananasStock = data["BananasStock"] # scalar parameter
ComboPackagesSold = model.addVar(vtype=gp.GRB.INTEGER, name="ComboPackagesSold")

model.addConstr(BananasCombo * ComboPackagesSold <= BananasStock, name="bananas_limit")

# Constraint: The total number of grapes in packages sold must not exceed the available grape stock
model.addConstr(GrapesBHPack * BananaHatersPackagesSold + GrapesCombo * ComboPackagesSold <= GrapesStock, "grape_stock_limit")

# Apple usage in banana-haters and combo packages does not exceed initial stock
model.addConstr(BananaHatersPackagesSold * ApplesBHPack + ComboPackagesSold * ApplesCombo <= ApplesStock, name="apple_stock_constraint")

# Ensure bananas used in combo packages do not exceed initial banana stock
model.addConstr(ComboPackagesSold * BananasCombo <= BananasStock, name="banana_usage_limit")

# The number of grapes used in banana-haters packages and combo packages does not exceed the initial stock
model.addConstr(BananaHatersPackagesSold * GrapesBHPack + ComboPackagesSold * GrapesCombo <= GrapesStock, 
                name="grapes_stock_constraint")

# Define the objective function
objective = BananaHatersPackagesSold * ProfitBHPack + ComboPackagesSold * ProfitCombo

# Set the objective
model.setObjective(objective, gp.GRB.MAXIMIZE)

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
