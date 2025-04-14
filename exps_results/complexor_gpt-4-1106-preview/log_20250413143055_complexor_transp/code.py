import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/complexor/transp/data.json", "r") as f:
    data = json.load(f)

NumberOfOrigins = data["NumberOfOrigins"] # scalar parameter
NumberOfDestinations = data["NumberOfDestinations"] # scalar parameter
SupplyOfOrigin = np.array(data["SupplyOfOrigin"]) # ['NumberOfOrigins']
DemandOfDestination = np.array(data["DemandOfDestination"]) # ['NumberOfDestinations']
CostPerUnit = np.array(data["CostPerUnit"]) # ['NumberOfOrigins', 'NumberOfDestinations']
ShippingQuantity = model.addVars(NumberOfOrigins, NumberOfDestinations, vtype=gp.GRB.CONTINUOUS, name="ShippingQuantity")

# Ensure that total supply shipped from each origin equals its available supply
for i in range(NumberOfOrigins):
    model.addConstr(gp.quicksum(ShippingQuantity[i, j] for j in range(NumberOfDestinations)) == SupplyOfOrigin[i], name="supply_constraint_origin_{}".format(i))

# Add demand satisfaction constraints for each destination
for j in range(NumberOfDestinations):
    model.addConstr(gp.quicksum(ShippingQuantity[i, j] for i in range(NumberOfOrigins)) == DemandOfDestination[j], name="demand_satisfaction_{}".format(j))

# Add non-negative shipping quantity constraints
for i in range(NumberOfOrigins):
    for j in range(NumberOfDestinations):
        model.addConstr(ShippingQuantity[i, j] >= 0, name=f"non_negative_shipping_{i}_{j}")

# Set objective
model.setObjective(gp.quicksum(CostPerUnit[i, j] * ShippingQuantity[i, j] for i in range(NumberOfOrigins) for j in range(NumberOfDestinations)), gp.GRB.MINIMIZE)

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
