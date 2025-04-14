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
Transactions = model.addVars(N, vtype=gp.GRB.CONTINUOUS, name="Transactions")
TransactionsFromTo = model.addVars(N, N, vtype=gp.GRB.CONTINUOUS, name="TransactionsFromTo")

# Add non-negativity constraint for Transactions
for i in range(N):
    model.addConstr(Transactions[i] >= 0, name=f"nonnegative_transactions_{i}")

# Add transaction limit constraints
for i in range(N):
    model.addConstr(Transactions[i] <= Limit[i], name=f"transaction_limit_{i}")

# Add transaction limit constraints
for i in range(N):
    model.addConstr(
        gp.quicksum(TransactionsFromTo[i, j] for j in range(N)) <= Limit[i],
        name=f"transaction_limit_{i}"
    )

# Add constraints to ensure total outgoing transactions do not exceed the available amount after accounting for incoming exchanges
for i in range(N):
    model.addConstr(
        gp.quicksum(TransactionsFromTo[i, j] for j in range(N)) <= Start[i] + gp.quicksum(Rate[j, i] * TransactionsFromTo[j, i] for j in range(N)),
        name=f"transaction_balance_{i}"
    )

# Set objective
model.setObjective(gp.quicksum(Start[i] + gp.quicksum(Rate[j, i] * TransactionsFromTo[j, i] for j in range(N)) - gp.quicksum(TransactionsFromTo[i, j] for j in range(N)) for i in range(N)), gp.GRB.MAXIMIZE)

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
