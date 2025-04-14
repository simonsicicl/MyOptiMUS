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
ItemSelection = model.addVars(TotalItems, vtype=gp.GRB.BINARY, name="ItemSelection")

# Add constraint for the maximum weight capacity of the knapsack
model.addConstr(gp.quicksum(ItemWeights[i] * ItemSelection[i] for i in range(TotalItems)) <= MaxKnapsackWeight, name="MaxKnapsackWeightConstraint")

TotalItems = data["TotalItems"] # scalar parameter
ItemSelection = model.addVars(TotalItems, vtype=gp.GRB.BINARY, name="ItemSelection")

# Limit the number of items selected to no more than TotalItems
model.addConstr(gp.quicksum(ItemSelection[i] for i in range(TotalItems)) <= TotalItems, name="limit_total_items")

# Add knapsack weight capacity constraint
knapsack_weight_constraint = gp.quicksum(ItemWeights[i] * ItemSelection[i] for i in range(TotalItems))
model.addConstr(knapsack_weight_constraint <= MaxKnapsackWeight, name="knapsack_weight")

# Define the objective function
model.setObjective(gp.quicksum(ItemValues[i] * ItemSelection[i] for i in range(TotalItems)), gp.GRB.MAXIMIZE)

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
