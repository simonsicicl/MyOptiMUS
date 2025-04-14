import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/13/data.json", "r") as f:
    data = json.load(f)

N = data["N"] # scalar parameter
Start = np.array(data["Start"]) # ['N']
Limit = np.array(data["Limit"]) # ['N']
Rate = np.array(data["Rate"]) # ['N', 'N']
TransactionsPerCurrency = model.addVars(N, vtype=gp.GRB.INTEGER, name="TransactionsPerCurrency")
FinalUnitsOfCurrency = model.addVars(N, vtype=gp.GRB.CONTINUOUS, name="FinalUnitsOfCurrency")
TransactionsPerCurrency = model.addVars(N, N, vtype=gp.GRB.CONTINUOUS, name="TransactionsPerCurrency")

# Constraint: Number of transactions for each currency is non-negative
for i in range(N):
    for j in range(N):
        model.addConstr(0 <= TransactionsPerCurrency[i, j], name=f"non_negative_transactions_{i}_{j}")

# Change the TransactionsPerCurrency variable to an integer type since its current definition collides with the second variable definition of the same name
for i in range(N):
    for j in range(N):
        TransactionsPerCurrency[i, j].vtype = gp.GRB.INTEGER

# Add constraints to ensure the number of transactions for each currency does not exceed the limit
for i in range(N):
    model.addConstr(TransactionsPerCurrency.sum(i, '*') <= Limit[i], name=f"transaction_limit_{i}")

# Add constraints for final units of currency to respect transaction limits and exchange rates
for i in range(N):
    model.addConstr(
        FinalUnitsOfCurrency[i] == Start[i] +
        gp.quicksum(TransactionsPerCurrency[j, i] * Rate[j, i] for j in range(N)) -
        gp.quicksum(TransactionsPerCurrency[i, j] * Rate[i, j] for j in range(N)),
        name=f"FinalUnitsOfCurrency_{i}"
    )

# Add transaction limit constraints for each currency
for i in range(N):
    model.addConstr(gp.quicksum(TransactionsPerCurrency[i, j] for j in range(N)) <= Limit[i], name="trans_limit_{}".format(i))

# There is no code needed here because the constraint defined is an inherent property of Gurobi variables.
# By default, Gurobi variables have a lower bound of 0, which aligns with our requirement.
# The variables 'TransactionsPerCurrency' for each currency pair (i, j) are already defined to be continuous
# and non-negative by their initial definition in the provided code.
# Therefore, no additional constraints are necessary to enforce this condition.

# Set objective
model.setObjective(gp.quicksum(FinalUnitsOfCurrency[i] for i in range(N)), gp.GRB.MAXIMIZE)

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
