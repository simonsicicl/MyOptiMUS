import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/complexor/TSP/data.json", "r") as f:
    data = json.load(f)

OriginNum = data["OriginNum"] # scalar parameter
DestinationNum = data["DestinationNum"] # scalar parameter
Supply = np.array(data["Supply"]) # ['OriginNum']
Demand = np.array(data["Demand"]) # ['DestinationNum']
Cost = np.array(data["Cost"]) # ['OriginNum', 'DestinationNum']
TransportedGoods = model.addVars(OriginNum, DestinationNum, vtype=gp.GRB.CONTINUOUS, name="TransportedGoods")

# Supply limit constraint at each origin
for i in range(OriginNum):
    model.addConstr(gp.quicksum(TransportedGoods[i, j] for j in range(DestinationNum)) <= Supply[i], name=f"supply_limit_origin_{i}")

# Ensure each destination meets its demand
for j in range(DestinationNum):
    model.addConstr(gp.quicksum(TransportedGoods[i, j] for i in range(OriginNum)) >= Demand[j], 
                    name=f"demand_constraint_{j}")

# Add non-negativity constraints for goods transported from any origin to any destination
for i in range(OriginNum):
    for j in range(DestinationNum):
        model.addConstr(TransportedGoods[i, j] >= 0, name="nonnegativity_constraint_{0}_{1}".format(i, j))

# Set objective function
model.setObjective(gp.quicksum(TransportedGoods[i, j] * Cost[i, j] for i in range(OriginNum) for j in range(DestinationNum)), gp.GRB.MINIMIZE)

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
