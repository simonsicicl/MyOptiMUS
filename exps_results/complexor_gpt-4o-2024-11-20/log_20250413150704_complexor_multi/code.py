import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/complexor/multi/data.json", "r") as f:
    data = json.load(f)

OriginNum = data["OriginNum"] # scalar parameter
DestinationNum = data["DestinationNum"] # scalar parameter
ProductNum = data["ProductNum"] # scalar parameter
Supply = np.array(data["Supply"]) # ['OriginNum', 'ProductNum']
Demand = np.array(data["Demand"]) # ['ProductNum', 'DestinationNum']
Limit = np.array(data["Limit"]) # ['OriginNum', 'DestinationNum']
Cost = np.array(data["Cost"]) # ['OriginNum', 'DestinationNum', 'ProductNum']
AmountShipped = model.addVars(OriginNum, DestinationNum, ProductNum, vtype=gp.GRB.CONTINUOUS, name="AmountShipped")

# Add constraints to ensure total amount shipped equals supply at each origin for each product
for i in range(OriginNum):
    for p in range(ProductNum):
        model.addConstr(
            gp.quicksum(AmountShipped[i, j, p] for j in range(DestinationNum)) == Supply[i, p],
            name=f"supply_balance_origin_{i}_product_{p}"
        )

# Add demand satisfaction constraints
for j in range(DestinationNum):
    for p in range(ProductNum):
        model.addConstr(
            gp.quicksum(AmountShipped[i, j, p] for i in range(OriginNum)) == Demand[p, j],
            name=f"demand_satisfaction_j{j}_p{p}"
        )

# Add constraints ensuring the total amount shipped from each origin i to each destination j does not exceed the limit
for i in range(OriginNum):
    for j in range(DestinationNum):
        model.addConstr(gp.quicksum(AmountShipped[i, j, p] for p in range(ProductNum)) <= Limit[i, j], name=f"shipment_limit_{i}_{j}")

# Add non-negativity constraints for AmountShipped
for i in range(OriginNum):
    for j in range(DestinationNum):
        for p in range(ProductNum):
            model.addConstr(AmountShipped[i, j, p] >= 0, name=f"nonnegativity_{i}_{j}_{p}")

# Set objective
model.setObjective(gp.quicksum(Cost[i, j, p] * AmountShipped[i, j, p] for i in range(OriginNum) for j in range(DestinationNum) for p in range(ProductNum)), gp.GRB.MINIMIZE)

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
