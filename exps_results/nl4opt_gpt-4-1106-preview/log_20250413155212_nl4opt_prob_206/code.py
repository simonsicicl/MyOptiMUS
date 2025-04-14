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
PlushToysPurchased = model.addVar(vtype=gp.GRB.INTEGER, name="PlushToysPurchased")
DollsPurchased = model.addVar(vtype=gp.GRB.INTEGER, name="DollsPurchased")

# Add constraint for the total cost of plush toys and dolls not exceeding MaxInventory
model.addConstr(CostPlush * PlushToysPurchased + CostDoll * DollsPurchased <= MaxInventory, name="max_inventory_constraint")

# Add constraint for minimum plush toys sold
model.addConstr(PlushToysPurchased >= MinPlushSold, name="min_plush_sold_constraint")



# Dolls to plush toys sold constraint
model.addConstr(DollsPurchased <= MaxDollsToPlushRatio * PlushToysPurchased, name="dolls_to_plush_ratio")

# Add constraint for non-negativity of the number of plush toys purchased
model.addConstr(PlushToysPurchased >= 0, name="non_negative_plush_toys_purchased")

# Constraint: The number of dolls purchased must be non-negative
model.addConstr(DollsPurchased >= 0, name="doll_purchase_non_negative")

# Define the objective function
model.setObjective(ProfitPlush * PlushToysPurchased + ProfitDoll * DollsPurchased, gp.GRB.MAXIMIZE)

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
