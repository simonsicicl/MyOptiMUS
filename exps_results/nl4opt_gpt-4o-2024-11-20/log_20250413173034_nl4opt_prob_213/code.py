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
RegularHandbagsSold = model.addVar(vtype=gp.GRB.CONTINUOUS, name="RegularHandbagsSold")
PremiumHandbagsSold = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PremiumHandbagsSold")

# Add non-negativity constraint for regular handbags sold
model.addConstr(RegularHandbagsSold >= 0, name="non_negativity_regular_handbags")

# The variable "PremiumHandbagsSold" is non-negative due to its default lower bound (0) in Gurobi.

# Add total manufacturing cost constraint
model.addConstr(
    CostRegular * RegularHandbagsSold + CostPremium * PremiumHandbagsSold <= Budget,
    name="total_manufacturing_cost"
)

# Add constraint to limit the total number of handbags sold
model.addConstr(RegularHandbagsSold + PremiumHandbagsSold <= MaxHandbags, name="limit_total_handbags_sold")

# Add budget constraint for manufacturing cost
model.addConstr(
    RegularHandbagsSold * CostRegular + PremiumHandbagsSold * CostPremium <= Budget,
    name="budget_constraint"
)

# Add sales capacity constraint
model.addConstr(RegularHandbagsSold + PremiumHandbagsSold <= MaxHandbags, name="sales_capacity")

# No additional code needed since RegularHandbagsSold is already defined as non-negative due to its default lower bound (0) in Gurobi.

# No additional code needed since PremiumHandbagsSold is already defined as non-negative due to its default lower bound (lb=0) in gurobipy.

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
