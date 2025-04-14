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
Shipment = model.addVars(OriginNum, DestinationNum, ProductNum, vtype=gp.GRB.CONTINUOUS, name="Shipment")

# Add constraints to ensure the total amount shipped equals the supply for each origin and product
for i in range(OriginNum):
    for p in range(ProductNum):
        model.addConstr(gp.quicksum(Shipment[i, j, p] for j in range(DestinationNum)) == Supply[i, p], 
                        name=f"supply_match_origin_{i}_product_{p}")

# Ensure total amount received at each destination for each product equals the demand for that product
for j in range(DestinationNum):
    for p in range(ProductNum):
        model.addConstr(
            gp.quicksum(Shipment[(i, j, p)] for i in range(OriginNum)) == Demand[p, j], 
            name=f"demand_constraint_dest{j}_prod{p}"
        )

# Add shipment limit constraints for each origin i and destination j
for i in range(OriginNum):
    for j in range(DestinationNum):
        model.addConstr(gp.quicksum(Shipment[i, j, p] for p in range(ProductNum)) <= Limit[i, j], 
                        name=f"ShipmentLimit_{i}_{j}")

# Add non-negativity constraints for all shipping quantities
for i in range(OriginNum):
    for j in range(DestinationNum):
        for p in range(ProductNum):
            model.addConstr(Shipment[i, j, p] >= 0, name="non_negativity_shipment[{}][{}][{}]".format(i, j, p))

# Set objective
model.setObjective(gp.quicksum(Shipment[i, j, p] * Cost[i, j, p] for i in range(OriginNum) for j in range(DestinationNum) for p in range(ProductNum)), gp.GRB.MINIMIZE)

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
