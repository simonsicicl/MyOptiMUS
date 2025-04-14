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
InvestmentCondo = model.addVar(vtype=gp.GRB.CONTINUOUS, name="InvestmentCondo")
InvestmentHouse = model.addVar(vtype=gp.GRB.CONTINUOUS, name="InvestmentHouse")

# Add constraint for the total investment in condos and houses not to exceed the total budget
model.addConstr(InvestmentCondo + InvestmentHouse <= TotalBudget, name="total_investment_constraint")

# Add constraint to ensure the investment in condos is at least MinPercentCondo of the total investment
model.addConstr(InvestmentCondo >= MinPercentCondo * (InvestmentCondo + InvestmentHouse), name="min_condo_investment")

# Add minimum investment constraint for detached houses
model.addConstr(InvestmentHouse >= MinInvestHouse, name="min_investment_house")

model.addConstr(InvestmentCondo >= 0, name="condos_non_negative")

# Add non-negativity constraint for investment in detached houses
model.addConstr(InvestmentHouse >= 0, name="investment_house_nonneg")

# Set objective
model.setObjective(ProfitCondo * InvestmentCondo + ProfitHouse * InvestmentHouse, gp.GRB.MAXIMIZE)

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
