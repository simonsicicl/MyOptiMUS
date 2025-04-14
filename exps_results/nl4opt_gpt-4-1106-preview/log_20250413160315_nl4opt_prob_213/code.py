import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_213/data.json", "r") as f:
    data = json.load(f)

ProfitRegular = data["ProfitRegular"] # scalar parameter
ProfitPremium = data["ProfitPremium"] # scalar parameter
CostRegular = data["CostRegular"] # scalar parameter
CostPremium = data["CostPremium"] # scalar parameter
Budget = data["Budget"] # scalar parameter
MaxHandbags = data["MaxHandbags"] # scalar parameter
RegularHandbagsSold = model.addVar(vtype=gp.GRB.INTEGER, name="RegularHandbagsSold")
PremiumHandbagsSold = model.addVar(vtype=gp.GRB.INTEGER, name="PremiumHandbagsSold")

# Since RegularHandbagsSold is already defined as an integer variable, no further code is needed to ensure its non-negativity.
# The constraint "RegularHandbagsSold >= 0" is inherently satisfied by the variable type definition.

# Since PremiumHandbagsSold is already an integer variable, no code is needed to enforce non-negativity
# The Gurobi optimizer enforces the non-negative constraint by default for integer variables.

# Add constraint for the total cost of manufacturing handbags not to exceed the budget
model.addConstr(CostRegular * RegularHandbagsSold + CostPremium * PremiumHandbagsSold <= Budget, name="budget_constraint")

model.addConstr(RegularHandbagsSold + PremiumHandbagsSold <= MaxHandbags, name="Max_Handbags_Sold_Constraint")

# Total cost of manufacturing handbags must not exceed the budget
model.addConstr(CostRegular * RegularHandbagsSold + CostPremium * PremiumHandbagsSold <= Budget, name="budget_constraint")

# Constraint: Total number of handbags sold should not exceed the maximum sales capacity
model.addConstr(RegularHandbagsSold + PremiumHandbagsSold <= MaxHandbags, name="max_sales_capacity")

# Set objective
model.setObjective(ProfitRegular * RegularHandbagsSold + ProfitPremium * PremiumHandbagsSold, gp.GRB.MAXIMIZE)

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
