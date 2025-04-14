import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/complexor/Knapsack/data.json", "r") as f:
    data = json.load(f)

TotalItems = data["TotalItems"] # scalar parameter
ItemValues = np.array(data["ItemValues"]) # ['TotalItems']
ItemWeights = np.array(data["ItemWeights"]) # ['TotalItems']
MaxKnapsackWeight = data["MaxKnapsackWeight"] # scalar parameter
ItemSelected = model.addVars(TotalItems, vtype=gp.GRB.BINARY, name="ItemSelected")

# Add knapsack weight constraint
model.addConstr(
    gp.quicksum(ItemWeights[i] * ItemSelected[i] for i in range(TotalItems)) <= MaxKnapsackWeight,
    name="knapsack_weight"
)

# No need for additional code to implement this constraint as it is already ensured by the binary nature of the ItemSelected variable.

# Add constraint to ensure the total number of selected items does not exceed TotalItems
model.addConstr(gp.quicksum(ItemSelected[i] for i in range(TotalItems)) <= TotalItems, name="total_items_limit")

# Binary constraint requires no additional code as it is already coded in the variable definition for ItemSelected.

# Add knapsack weight constraint
model.addConstr(
    gp.quicksum(ItemSelected[i] * ItemWeights[i] for i in range(TotalItems)) <= MaxKnapsackWeight,
    name="knapsack_weight_constraint"
)

# Set objective
model.setObjective(gp.quicksum(ItemValues[i] * ItemSelected[i] for i in range(TotalItems)), gp.GRB.MAXIMIZE)

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
