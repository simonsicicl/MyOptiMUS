import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/61/data.json", "r") as f:
    data = json.load(f)

T = data["T"] # scalar parameter
Demands = np.array(data["Demands"]) # ['T']
UnloadCosts = np.array(data["UnloadCosts"]) # ['T']
UnloadCapacity = np.array(data["UnloadCapacity"]) # ['T']
HoldingCost = data["HoldingCost"] # scalar parameter
MaxContainer = data["MaxContainer"] # scalar parameter
InitContainer = data["InitContainer"] # scalar parameter
NumCranes = data["NumCranes"] # scalar parameter
CraneCapacity = data["CraneCapacity"] # scalar parameter
CraneCost = data["CraneCost"] # scalar parameter
ContainersUnloaded = model.addVars(T, vtype=gp.GRB.INTEGER, name="ContainersUnloaded")
InventoryLevel = model.addVars(T, vtype=gp.GRB.CONTINUOUS, name="InventoryLevel")
CranesUsed = model.addVars(T, vtype=gp.GRB.INTEGER, name="CranesUsed")

# Demands must be met for each time period t
for t in range(T):
    model.addConstr((gp.quicksum(ContainersUnloaded[t_prime] for t_prime in range(t)) + InitContainer -
                     gp.quicksum(Demands[t_prime] for t_prime in range(t))) >= 0, name=f"demand_met_{t}")

# Add unloading capacity constraints for each time period t
for t in range(T):
    model.addConstr(ContainersUnloaded[t] <= UnloadCapacity[t], name=f"unloading_capacity_{t}")

# Add inventory level constraints
for t in range(T):
    model.addConstr(InventoryLevel[t] <= MaxContainer, name=f"InventoryLevel_{t}")

# Add initial inventory level constraint
model.addConstr(InventoryLevel[0] == InitContainer, name="init_inventory_level")

# Inventory balance constraints
for t in range(1, T):
    model.addConstr(InventoryLevel[t] == InventoryLevel[t-1] + ContainersUnloaded[t] - Demands[t], name=f"inventory_balance_{t}")

# Ensure that cranes used at time period t are sufficient for the containers unloaded
for t in range(T):
    model.addConstr(CranesUsed[t] * CraneCapacity >= ContainersUnloaded[t], name=f"crane_capacity_t{t}")

# Add constraints to ensure that the number of cranes used does not exceed the total number of cranes available
for t in range(T):
    model.addConstr(CranesUsed[t] <= NumCranes, name=f"CranesUsed_limit_{t}")

# Define the objective function
model.setObjective(
    gp.quicksum(
        UnloadCosts[t] * ContainersUnloaded[t] + 
        HoldingCost * InventoryLevel[t] + 
        CraneCost * CranesUsed[t]
    for t in range(T)),
    gp.GRB.MINIMIZE
)

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
