import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_9/data.json", "r") as f:
    data = json.load(f)

Budget = data["Budget"] # scalar parameter
CostCarrot = data["CostCarrot"] # scalar parameter
CostCucumber = data["CostCucumber"] # scalar parameter
ProfitCarrot = data["ProfitCarrot"] # scalar parameter
ProfitCucumber = data["ProfitCucumber"] # scalar parameter
RatioCucumbersToCarrots = data["RatioCucumbersToCarrots"] # scalar parameter
MinCarrotsSold = data["MinCarrotsSold"] # scalar parameter
MaxCarrotsSold = data["MaxCarrotsSold"] # scalar parameter
CarrotsSold = model.addVar(vtype=gp.GRB.INTEGER, name="CarrotsSold")
CucumbersSold = model.addVar(vtype=gp.GRB.INTEGER, name="CucumbersSold")

# Since the variable "CarrotsSold" is already defined as an integer variable, no additional constraints are needed.

# No additional code needed since the variable 'CucumbersSold' has already been defined as an integer.

# Since CarrotsSold has already been added as a non-negative integer var, no constraint required
# CarrotsSold >= 0 is implicit in its declaration as a non-negative integer.

# No code needed as the variable CucumbersSold is already defined as non-negative by its type being INTEGER

# Add budget constraint for the total cost of carrots and cucumbers
model.addConstr(CostCarrot * CarrotsSold + CostCucumber * CucumbersSold <= Budget, name="budget_constraint")

# Ensure that cucumbers sold do not exceed the maximum ratio of cucumbers to carrots sold times the number of carrots sold
model.addConstr(CucumbersSold <= RatioCucumbersToCarrots * CarrotsSold, name="cucumber_carrot_ratio_constraint")

# Ensure that the number of carrots sold is greater than or equal to the minimum required number of carrots to be sold
model.addConstr(CarrotsSold >= MinCarrotsSold, name="min_carrots_sold_constraint")

# Constraint: The number of carrots sold must not exceed the maximum allowed
model.addConstr(CarrotsSold <= MaxCarrotsSold, name="max_carrots_sold")

# Set objective
model.setObjective(ProfitCarrot * CarrotsSold + ProfitCucumber * CucumbersSold, gp.GRB.MAXIMIZE)

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
