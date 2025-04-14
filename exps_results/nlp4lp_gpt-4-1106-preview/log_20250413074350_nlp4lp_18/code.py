import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/18/data.json", "r") as f:
    data = json.load(f)

N = data["N"] # scalar parameter
Bought = np.array(data["Bought"]) # ['N']
BuyPrice = np.array(data["BuyPrice"]) # ['N']
CurrentPrice = np.array(data["CurrentPrice"]) # ['N']
FuturePrice = np.array(data["FuturePrice"]) # ['N']
TransactionRate = data["TransactionRate"] # scalar parameter
TaxRate = data["TaxRate"] # scalar parameter
K = data["K"] # scalar parameter
SharesSold = model.addVars(N, vtype=gp.GRB.INTEGER, name="SharesSold")
TaxableAmount = model.addVars(N, vtype=gp.GRB.CONTINUOUS, name="TaxableAmount")

# Ensure that shares sold by the investor are non-negative
for i in range(N):
    model.addConstr(SharesSold[i] >= 0, name=f"non_negativity_shares_sold_{i}")

# Add constraints that ensure number of shares sold is less than or equal to the shares bought for each asset
for i in range(N):
    model.addConstr(SharesSold[i] <= Bought[i], name=f"shares_limit_{i}")

# Net amount raised from selling shares constraint
net_amount_expr = gp.quicksum((CurrentPrice[i] * SharesSold[i] -
                               TransactionRate * SharesSold[i] * CurrentPrice[i] -
                               TaxRate * SharesSold[i] * max(0, CurrentPrice[i] - BuyPrice[i]))
                              for i in range(N))
model.addConstr(net_amount_expr >= K, name="net_amount_raised")

# Taxable amount computation constraints based on profit per share
for i in range(N):
    profit_per_share = model.addVar(vtype=gp.GRB.CONTINUOUS, name=f"profit_per_share_{i}")
    model.addConstr(profit_per_share == gp.max_(CurrentPrice[i] - BuyPrice[i], 0), name=f"profit_per_share_max_{i}")
    model.addConstr(TaxableAmount[i] == profit_per_share * SharesSold[i], name=f"taxable_amount_{i}")

# Add constraint for taxable amount calculation for each share sold
for i in range(N):
    model.addConstr(TaxableAmount[i] == gp.max_(0, CurrentPrice[i] - BuyPrice[i]), name="taxable_amount_calculation")

# Ensure investor raises at least the amount of money they need after accounting for taxes and transaction costs
investor_constraint = gp.quicksum(
    SharesSold[i] * (CurrentPrice[i] - TaxableAmount[i] * TaxRate - TransactionRate * CurrentPrice[i])
    for i in range(N)
) >= K
model.addConstr(investor_constraint, name="investor_funds_raised")

# Add constraints to calculate the taxable amount for each share sold\nCurrentPrice = model.addVars(N, vtype=gp.GRB.CONTINUOUS, name=\"CurrentPrice\")\nBuyPrice = model.addVars(N, vtype=gp.GRB.CONTINUOUS, name=\"BuyPrice\")\nfor i in range(N):\n    model.addGenConstrMax(TaxableAmount[i], [CurrentPrice[i] - BuyPrice[i], 0], name=f\"taxable_amount_{i}\")

# Set objective
model.setObjective(gp.quicksum((Bought[i] - SharesSold[i]) * FuturePrice[i] for i in range(N)), gp.GRB.MAXIMIZE)

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
