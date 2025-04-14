import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/56/data.json", "r") as f:
    data = json.load(f)

NumTerminals = data["NumTerminals"] # scalar parameter
NumDestinations = data["NumDestinations"] # scalar parameter
Cost = np.array(data["Cost"]) # ['NumTerminals', 'NumDestinations']
Demand = np.array(data["Demand"]) # ['NumDestinations']
Supply = np.array(data["Supply"]) # ['NumTerminals']
QuantityTransported = model.addVars(NumTerminals, NumDestinations, vtype=gp.GRB.CONTINUOUS, name="QuantityTransported")

# The transported quantity constraint does not require additional code as the non-negativity is inherently enforced by the variable type (GRB.CONTINUOUS), which is defined to be non-negative by default.

# Add constraints ensuring the transported quantity from each terminal does not exceed its supply
for i in range(NumTerminals):
    model.addConstr(
        gp.quicksum(QuantityTransported[i, j] for j in range(NumDestinations)) <= Supply[i], 
        name=f"supply_limit_terminal_{i}"
    )

# Add constraints to ensure the transported quantity from all terminals to a destination meets its demand
for j in range(NumDestinations):
    model.addConstr(
        gp.quicksum(QuantityTransported[i, j] for i in range(NumTerminals)) == Demand[j],
        name=f"demand_satisfaction_dest{j}")

# Add demand satisfaction constraints for each destination
for j in range(NumDestinations):
    model.addConstr(
        gp.quicksum(QuantityTransported[i, j] for i in range(NumTerminals)) >= Demand[j],
        name=f"demand_satisfaction_dest_{j}"
    )

# Add supply constraints for each terminal
for i in range(NumTerminals):
    model.addConstr(
        gp.quicksum(QuantityTransported[i, j] for j in range(NumDestinations)) <= Supply[i],
        name=f"supply_constraint_terminal_{i}"
    )

# Ensure that the quantity transported on each route is non-negative
for i in range(NumTerminals):
    for j in range(NumDestinations):
        model.addConstr(QuantityTransported[i, j] >= 0, name=f"non_negative_transport_{i}_{j}")

# Set objective
model.setObjective(gp.quicksum(Cost[i, j] * QuantityTransported[i, j] 
                               for i in range(NumTerminals) for j in range(NumDestinations)), 
                   gp.GRB.MINIMIZE)

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
