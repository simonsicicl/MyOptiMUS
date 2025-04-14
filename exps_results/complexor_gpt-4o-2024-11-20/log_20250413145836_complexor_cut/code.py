import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/complexor/cut/data.json", "r") as f:
    data = json.load(f)

NumWidths = data["NumWidths"] # scalar parameter
NumPatterns = data["NumPatterns"] # scalar parameter
Widths = np.array(data["Widths"]) # ['NumWidths']
RollWidth = data["RollWidth"] # scalar parameter
Orders = np.array(data["Orders"]) # ['NumWidths']
NumRollsWidthPattern = np.array(data["NumRollsWidthPattern"]) # ['NumWidths', 'NumPatterns']
PatternsUsed = model.addVars(NumPatterns, vtype=gp.GRB.INTEGER, name="PatternsUsed")

# Add constraints ensuring the total number of rolls produced for each width is non-negative
for i in range(NumWidths):
    model.addConstr(
        gp.quicksum(NumRollsWidthPattern[i, j] * PatternsUsed[j] for j in range(NumPatterns)) >= 0, 
        name=f"non_negative_rolls_width_{i}"
    )

# Add constraints to ensure total rolls cut for each width i meet or exceed orders
for i in range(NumWidths):
    model.addConstr(
        gp.quicksum(NumRollsWidthPattern[i, j] * PatternsUsed[j] for j in range(NumPatterns)) >= Orders[i],
        name=f"meet_order_width_{i}"
    )

# Non-negativity constraint for number of rolls cut
for j in range(NumPatterns):
    model.addConstr(PatternsUsed[j] >= 0, name=f"non_negativity_pattern_{j}")

# Add constraints to ensure orders for each width are satisfied by the cutting patterns used
for i in range(NumWidths):
    model.addConstr(
        gp.quicksum(NumRollsWidthPattern[i, j] * PatternsUsed[j] for j in range(NumPatterns)) >= Orders[i],
        name=f"OrderSatisfaction_width{i}"
    )

# Set objective
model.setObjective(gp.quicksum(PatternsUsed[j] for j in range(NumPatterns)), gp.GRB.MINIMIZE)

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
