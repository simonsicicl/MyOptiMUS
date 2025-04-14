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
UnloadedQuantity = model.addVars(T, vtype=gp.GRB.CONTINUOUS, name="UnloadedQuantity")
Inventory = model.addVars(T, vtype=gp.GRB.CONTINUOUS, name="Inventory")
ExtraCranes = model.addVars(T, vtype=gp.GRB.CONTINUOUS, name="ExtraCranes")

for t in range(T):
    if t == 0:
        model.addConstr(
            UnloadedQuantity[t] == Demands[t] + Inventory[t],
            name=f'demand_balance_{t}'
        )
    else:
        model.addConstr(
            Inventory[t] + UnloadedQuantity[t] == Demands[t] + Inventory[t - 1],
            name=f'demand_balance_{t}'
        )

# Add unloading capacity constraints
for t in range(T):
    model.addConstr(UnloadedQuantity[t] <= UnloadCapacity[t], name=f"unloading_capacity_{t}")

# Add maximum container inventory constraints
for t in range(T):
    model.addConstr(Inventory[t] <= MaxContainer, name=f"max_inventory_{t}")

# Add unloading capacity constraints
for t in range(T):
    model.addConstr(UnloadedQuantity[t] <= UnloadCapacity[t], name=f"unloading_capacity_{t}")

# Add constraint to ensure inventory does not exceed maximum storage capacity
for t in range(T):
    model.addConstr(Inventory[t] <= MaxContainer, name=f"storage_capacity_t{t}")

# Set the initial inventory constraint
model.addConstr(Inventory[0] == InitContainer, name="initial_inventory")

# Add inventory balance constraints
model.addConstr(Inventory[0] == InitContainer, name="initial_inventory")

for t in range(1, T):
    model.addConstr(
        Inventory[t] == Inventory[t - 1] + UnloadedQuantity[t] - Demands[t],
        name=f"inventory_balance_{t}"
    )

# Add inventory balance constraints
for t in range(T):
    if t == 0:
        # Initial condition for time period 1
        model.addConstr(UnloadedQuantity[t] - Demands[t] == Inventory[t], name=f"inventory_balance_{t}")
    else:
        # Balance constraint for all other time periods
        model.addConstr(
            Inventory[t - 1] + UnloadedQuantity[t] - Demands[t] == Inventory[t],
            name=f"inventory_balance_{t}"
        )

# Add unloading capacity constraints
for t in range(T):
    model.addConstr(
        UnloadedQuantity[t] <= (NumCranes + ExtraCranes[t]) * CraneCapacity,
        name=f"unloading_capacity_t{t}"
    )

# Add inventory capacity constraints
for t in range(T):
    model.addConstr(Inventory[t] <= MaxContainer, name=f"inventory_capacity_{t}")

# Add non-negativity constraints for ExtraCranes
for t in range(T):
    model.addConstr(ExtraCranes[t] >= 0, name=f"non_negativity_ExtraCranes_{t}")

# Set objective
model.setObjective(
    gp.quicksum(UnloadCosts[t] * UnloadedQuantity[t] for t in range(T)) +
    gp.quicksum(HoldingCost * Inventory[t] for t in range(T)) +
    gp.quicksum(CraneCost * ExtraCranes[t] for t in range(T)), 
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
