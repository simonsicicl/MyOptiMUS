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
GoodsTransported = model.addVars(OriginNum, DestinationNum, vtype=gp.GRB.CONTINUOUS, name="GoodsTransported")

# Add supply limit constraints for each origin
for i in range(OriginNum):
    model.addConstr(
        gp.quicksum(GoodsTransported[i, j] for j in range(DestinationNum)) <= Supply[i],
        name=f"supply_limit_origin_{i}"
    )

# Add constraints to ensure demand is met at each destination
for j in range(DestinationNum):
    model.addConstr(gp.quicksum(GoodsTransported[i, j] for i in range(OriginNum)) == Demand[j], name=f"demand_satisfaction_dest_{j}")

# Non-negativity constraint for GoodsTransported variables
for i in range(OriginNum):
    for j in range(DestinationNum):
        model.addConstr(GoodsTransported[i, j] >= 0, name=f"non_negative_GoodsTransported_{i}_{j}")

# Add constraints to ensure total goods transported from each origin does not exceed its supply limit
for i in range(OriginNum):
    model.addConstr(
        gp.quicksum(GoodsTransported[i, j] for j in range(DestinationNum)) <= Supply[i],
        name=f"supply_limit_origin_{i}"
    )

# Ensure the total goods transported to each destination meets its demand
for j in range(DestinationNum):
    model.addConstr(
        gp.quicksum(GoodsTransported[i, j] for i in range(OriginNum)) == Demand[j],
        name=f"demand_satisfaction_{j}"
    )

# Ensure non-negativity of the transported goods
for i in range(OriginNum):
    for j in range(DestinationNum):
        model.addConstr(GoodsTransported[i, j] >= 0, name=f"nonnegativity_transport_{i}_{j}")

# Set objective
model.setObjective(gp.quicksum(Cost[i, j] * GoodsTransported[i, j] for i in range(OriginNum) for j in range(DestinationNum)), gp.GRB.MINIMIZE)

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
