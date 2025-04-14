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
CarrotsSold = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CarrotsSold")
CucumbersSold = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CucumbersSold")

# Modify the variable CarrotsSold to enforce integrality
CarrotsSold.vtype = gp.GRB.INTEGER

# Change the variable type to integer to ensure CucumbersSold is an integer
CucumbersSold.vtype = gp.GRB.INTEGER

# Since the variable "CarrotsSold" is already coded as non-negative (continuous variables in gurobipy are non-negative by default), no additional constraint is needed.

# The variable "CucumbersSold" is already defined as non-negative due to its default non-negativity in Gurobi,
# so no constraint code is needed.

# Add budget constraint
model.addConstr(CostCarrot * CarrotsSold + CostCucumber * CucumbersSold <= Budget, name="budget_constraint")

# Add constraint ensuring that the number of cucumbers sold does not exceed the ratio times the number of carrots sold
model.addConstr(CucumbersSold <= RatioCucumbersToCarrots * CarrotsSold, name="cucumber_to_carrot_ratio")

# Add constraint to ensure the number of carrots sold meets or exceeds the specified minimum
model.addConstr(CarrotsSold >= MinCarrotsSold, name="min_carrots_sold")

# Add constraint to ensure the number of carrots sold does not exceed the maximum allowed
model.addConstr(CarrotsSold <= MaxCarrotsSold, name="max_carrots_sold_constraint")

# Add constraint for bounding the number of carrots sold
model.addConstr(MinCarrotsSold <= CarrotsSold, name="min_carrots_sold")
model.addConstr(CarrotsSold <= MaxCarrotsSold, name="max_carrots_sold")

# Add the cucumbers-to-carrots ratio constraint
model.addConstr(CucumbersSold <= RatioCucumbersToCarrots * CarrotsSold, name="cucumber_to_carrot_ratio")

# Add budget constraint for carrots and cucumbers
model.addConstr(CarrotsSold * CostCarrot + CucumbersSold * CostCucumber <= Budget, name="budget_constraint")

# Add constraint to ensure the number of cucumbers sold does not exceed the specified ratio of carrots sold
model.addConstr(CucumbersSold <= RatioCucumbersToCarrots * CarrotsSold, name="cucumber_to_carrot_ratio")

# Add constraint to ensure the number of carrots sold is within the allowable range
model.addConstr(MinCarrotsSold <= CarrotsSold, name="min_carrots_sold")
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
