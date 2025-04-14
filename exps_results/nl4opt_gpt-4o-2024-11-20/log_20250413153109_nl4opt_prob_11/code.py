import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_11/data.json", "r") as f:
    data = json.load(f)

TotalBudget = data["TotalBudget"] # scalar parameter
ProfitCondo = data["ProfitCondo"] # scalar parameter
ProfitHouse = data["ProfitHouse"] # scalar parameter
MinPercentCondo = data["MinPercentCondo"] # scalar parameter
MinInvestHouse = data["MinInvestHouse"] # scalar parameter
InvestCondo = model.addVar(vtype=gp.GRB.CONTINUOUS, name="InvestCondo")
InvestHouse = model.addVar(vtype=gp.GRB.CONTINUOUS, name="InvestHouse")

# Add total investment constraint
model.addConstr(InvestCondo + InvestHouse <= TotalBudget, name="total_investment_constraint")

# Add constraint ensuring investment in condos meets minimum percentage requirement
model.addConstr((1 - MinPercentCondo) * InvestCondo >= MinPercentCondo * InvestHouse, name="min_condo_investment")

# Add minimum investment constraint for detached houses
model.addConstr(InvestHouse >= MinInvestHouse, name="min_invest_house")

# The non-negativity of InvestCondo is already defined through its lower bound of zero in the variable definition.

# The investment in detached houses is already non-negative since it is defined as a continuous variable which is inherently non-negative in Gurobi.

# Add constraint to ensure total investments do not exceed the total budget
model.addConstr(InvestCondo + InvestHouse <= TotalBudget, name="investment_budget_constraint")

# Add constraint ensuring at least the minimum percentage of the total budget is invested in condos
model.addConstr(InvestCondo >= MinPercentCondo * TotalBudget, name="min_investment_condos")

# Add constraint ensuring investment in detached houses meets the minimum required amount
model.addConstr(InvestHouse >= MinInvestHouse, name="min_invest_house")

# Set objective
model.setObjective(ProfitCondo * InvestCondo + ProfitHouse * InvestHouse, gp.GRB.MAXIMIZE)

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
