import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_206/data.json", "r") as f:
    data = json.load(f)

CostPlush = data["CostPlush"] # scalar parameter
CostDoll = data["CostDoll"] # scalar parameter
MaxInventory = data["MaxInventory"] # scalar parameter
ProfitPlush = data["ProfitPlush"] # scalar parameter
ProfitDoll = data["ProfitDoll"] # scalar parameter
MinPlushSold = data["MinPlushSold"] # scalar parameter
MaxPlushSold = data["MaxPlushSold"] # scalar parameter
MaxDollsToPlushRatio = data["MaxDollsToPlushRatio"] # scalar parameter
NumPlush = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumPlush")
NumDoll = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumDoll")
NumPlushSold = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumPlushSold")
NumDollSold = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumDollSold")

# Add constraint for the total cost of plush toys and dolls purchased being at most the maximum inventory budget
model.addConstr(CostPlush * NumPlush + CostDoll * NumDoll <= MaxInventory, name="inventory_budget_constraint")

# Add constraint to ensure the number of plush toys sold is at least MinPlushSold  
model.addConstr(NumPlushSold >= MinPlushSold, name="min_plush_sold_constraint")

# Add constraint to ensure the number of plush toys sold does not exceed the maximum limit
model.addConstr(NumPlushSold <= MaxPlushSold, name="plush_toy_sales_limit")

# Add constraint ensuring the number of dolls sold is at most MaxDollsToPlushRatio times the number of plush toys sold
model.addConstr(NumDollSold <= MaxDollsToPlushRatio * NumPlushSold, name="dolls_to_plush_ratio")

# Non-negativity constraint for the number of plush toys
model.addConstr(NumPlush >= 0, name="non_negativity_NumPlush")

# Add constraint to ensure the number of dolls purchased by the toy store owner is non-negative
model.addConstr(NumDoll >= 0, name="non_negative_dolls")

# Add constraint ensuring the number of plush toys sold does not exceed the number of plush toys purchased
model.addConstr(NumPlushSold <= NumPlush, name="plush_sales_limit")

# Add constraint to limit the number of plush toys sold
model.addConstr(NumPlushSold <= MaxPlushSold, name="limit_plush_sales")

# Add inventory spending constraint
model.addConstr(CostPlush * NumPlush + CostDoll * NumDoll <= MaxInventory, name="inventory_budget")

# Add constraint ensuring the number of plush toys sold does not exceed the number of plush toys purchased
model.addConstr(NumPlushSold <= NumPlush, name="plush_sales_limit")

# Add constraint: The number of dolls sold cannot exceed the number of dolls purchased
model.addConstr(NumDollSold <= NumDoll, name="doll_sales_limit")

# Add constraints to ensure the number of plush toys sold lies within the sales bounds
model.addConstr(NumPlushSold >= MinPlushSold, name="min_plush_sold")
model.addConstr(NumPlushSold <= MaxPlushSold, name="max_plush_sold")

# Add constraint to ensure the number of dolls sold satisfies the maximum ratio to plush toys sold
model.addConstr(NumDollSold <= MaxDollsToPlushRatio * NumPlushSold, name="max_dolls_to_plush_ratio")

# Set objective
model.setObjective(ProfitPlush * NumPlushSold + ProfitDoll * NumDollSold, gp.GRB.MAXIMIZE)

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
