import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/19/data.json", "r") as f:
    data = json.load(f)

M = data["M"] # scalar parameter
I = data["I"] # scalar parameter
BuyPrice = np.array(data["BuyPrice"]) # ['M', 'I']
SellPrice = data["SellPrice"] # scalar parameter
IsVegetable = np.array(data["IsVegetable"]) # ['I']
MaxVegetableRefiningPerMonth = data["MaxVegetableRefiningPerMonth"] # scalar parameter
MaxNonVegetableRefiningPerMonth = data["MaxNonVegetableRefiningPerMonth"] # scalar parameter
StorageSize = data["StorageSize"] # scalar parameter
StorageCost = data["StorageCost"] # scalar parameter
MaxHardness = data["MaxHardness"] # scalar parameter
MinHardness = data["MinHardness"] # scalar parameter
Hardness = np.array(data["Hardness"]) # ['I']
InitialAmount = data["InitialAmount"] # scalar parameter
ItemsBought = model.addVars(M, I, vtype=gp.GRB.CONTINUOUS, name="ItemsBought")
ItemsStored = model.addVars(M, I, vtype=gp.GRB.CONTINUOUS, name="ItemsStored")
ItemsSold = model.addVars(M, I, vtype=gp.GRB.CONTINUOUS, name="ItemsSold")
ItemsRefined = model.addVars(M, I, vtype=gp.GRB.CONTINUOUS, name="ItemsRefined")
TotalHardnessPerMonth = model.addVars(M, vtype=gp.GRB.CONTINUOUS, name="TotalHardnessPerMonth")

# Non-negativity constraints for ItemsBought, ItemsStored, and ItemsSold
for m in range(M):
    for i in range(I):
        model.addConstr(ItemsBought[m, i] >= 0, name=f"NonNeg_ItemsBought_{m}_{i}")
        model.addConstr(ItemsStored[m, i] >= 0, name=f"NonNeg_ItemsStored_{m}_{i}")
        model.addConstr(ItemsSold[m, i] >= 0, name=f"NonNeg_ItemsSold_{m}_{i}")

# Add weighted average hardness constraints
for m in range(M):
    model.addConstr(
        gp.quicksum(ItemsRefined[m, i] * Hardness[i] for i in range(I)) 
        >= MinHardness * gp.quicksum(ItemsRefined[m, i] for i in range(I)), 
        name=f"min_hardness_month_{m}"
    )

# Add hardness constraints to ensure the total hardness per month does not exceed maximum allowable hardness
for m in range(M):
    model.addConstr(
        TotalHardnessPerMonth[m] == gp.quicksum(ItemsRefined[m, i] * Hardness[i] for i in range(I)),
        name=f"calc_total_hardness_month_{m}"
    )
    model.addConstr(
        TotalHardnessPerMonth[m] <= MaxHardness,
        name=f"hardness_limit_month_{m}"
    )

# Add vegetable refining constraints
for m in range(M):
    model.addConstr(
        gp.quicksum(ItemsRefined[m, i] * IsVegetable[i] for i in range(I)) <= MaxVegetableRefiningPerMonth,
        name=f"vegetable_refining_limit_{m}"
    )

# Add constraints for limiting non-vegetable refining per month
for m in range(M):
    model.addConstr(
        gp.quicksum((1 - IsVegetable[i]) * ItemsRefined[m, i] for i in range(I)) <= MaxNonVegetableRefiningPerMonth,
        name=f"NonVegetableRefiningLimit_month_{m}"
    )

# Add total storage usage constraints
for m in range(M):
    model.addConstr(gp.quicksum(ItemsStored[m, i] for i in range(I)) <= StorageSize, name=f"storage_limit_month_{m}")

# Add constraint to ensure StorageSize accommodates InitialAmount
model.addConstr(InitialAmount <= StorageSize, name="storage_initial_constraint")

# Add monthly vegetable refining capacity constraints
for m in range(M):
    model.addConstr(
        gp.quicksum(ItemsRefined[m, i] * IsVegetable[i] for i in range(I)) <= MaxVegetableRefiningPerMonth,
        name=f"vegetable_refining_capacity_month_{m}"
    )

# Add constraints to ensure non-vegetable refining does not exceed the maximum refining capacity per month
for m in range(M):
    model.addConstr(
        gp.quicksum(ItemsRefined[m, i] * (1 - IsVegetable[i]) for i in range(I)) <= MaxNonVegetableRefiningPerMonth,
        name=f"max_non_vegetable_refining_month_{m}"
    )

# Add constraint to compute TotalHardnessPerMonth
for m in range(M):
    model.addConstr(
        TotalHardnessPerMonth[m] == gp.quicksum(Hardness[i] * ItemsRefined[m, i] for i in range(I)),
        name=f"TotalHardnessPerMonth_{m+1}"
    )

# Add storage balance constraints
for i in range(I):
    for m in range(1, M):  # Starting from month 1 since month 0 is the initial inventory
        model.addConstr(
            ItemsStored[m, i] == ItemsStored[m - 1, i] + ItemsBought[m, i] - ItemsSold[m, i] - ItemsRefined[m, i],
            name=f"storage_balance_m{m}_i{i}"
        )

# Add hardness constraints
for m in range(M):
    model.addConstr(
        MinHardness <= gp.quicksum(ItemsRefined[m, i] * Hardness[i] for i in range(I)),
        name=f"min_hardness_{m}"
    )
    model.addConstr(
        gp.quicksum(ItemsRefined[m, i] * Hardness[i] for i in range(I)) <= MaxHardness,
        name=f"max_hardness_{m}"
    )

# Add vegetable refining capacity constraints
for m in range(M):
    model.addConstr(
        gp.quicksum(ItemsRefined[m, i] for i in range(I) if IsVegetable[i] == 1)
        <= MaxVegetableRefiningPerMonth,
        name=f"vegetable_refining_capacity_{m}"
    )

# Add non-vegetable refining capacity constraints
for m in range(M):
    model.addConstr(
        gp.quicksum(ItemsRefined[m, i] for i in range(I) if IsVegetable[i] == 0) <= MaxNonVegetableRefiningPerMonth,
        name=f"non_vegetable_refining_capacity_{m}"
    )

# Add storage capacity constraints
for m in range(M):
    model.addConstr(gp.quicksum(ItemsStored[m, i] for i in range(I)) <= StorageSize, name=f"storage_capacity_{m}")

# Set objective
model.setObjective(
    gp.quicksum(ItemsSold[m, i] * SellPrice for m in range(M) for i in range(I)) -
    (
        gp.quicksum(ItemsBought[m, i] * BuyPrice[m, i] for m in range(M) for i in range(I)) +
        gp.quicksum(ItemsStored[m, i] * StorageCost for m in range(M) for i in range(I))
    ),
    gp.GRB.MAXIMIZE
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
