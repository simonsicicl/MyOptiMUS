import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_146/data.json", "r") as f:
    data = json.load(f)

BlueberryAntioxidants = data["BlueberryAntioxidants"] # scalar parameter
BlueberryMinerals = data["BlueberryMinerals"] # scalar parameter
StrawberryAntioxidants = data["StrawberryAntioxidants"] # scalar parameter
StrawberryMinerals = data["StrawberryMinerals"] # scalar parameter
MinAntioxidants = data["MinAntioxidants"] # scalar parameter
MinMinerals = data["MinMinerals"] # scalar parameter
StrawberryBlueberryRatio = data["StrawberryBlueberryRatio"] # scalar parameter
BlueberrySugar = data["BlueberrySugar"] # scalar parameter
StrawberrySugar = data["StrawberrySugar"] # scalar parameter
BlueberryPacks = model.addVar(vtype=gp.GRB.CONTINUOUS, name="BlueberryPacks")
StrawberryPacks = model.addVar(vtype=gp.GRB.CONTINUOUS, name="StrawberryPacks")

# The non-negativity of BlueberryPacks is defined inherently by its lower bound.
# No additional constraints are needed as Gurobi variables are non-negative by default unless explicitly modified.

# The variable StrawberryPacks is defined with non-negativity (vtype=gp.GRB.CONTINUOUS), so no constraint is needed.

# Add antioxidant requirement constraint
model.addConstr(
    BlueberryPacks * BlueberryAntioxidants + StrawberryPacks * StrawberryAntioxidants >= MinAntioxidants, 
    name="antioxidant_requirement"
)

# Add constraint to ensure total minerals from blueberries and strawberries meet the minimum requirement
model.addConstr(
    BlueberryPacks * BlueberryMinerals + StrawberryPacks * StrawberryMinerals >= MinMinerals,
    name="min_minerals_constraint"
)

# Add constraint ensuring the number of strawberry packs is at least 3 times the number of blueberry packs
model.addConstr(StrawberryPacks >= 3 * BlueberryPacks, name="strawberry_blueberry_ratio")

# Add constraint for minimum anti-oxidant intake
model.addConstr(
    BlueberryAntioxidants * BlueberryPacks + StrawberryAntioxidants * StrawberryPacks >= MinAntioxidants,
    name="min_antioxidants_requirement"
)

# Ensure the total mineral intake meets the minimum requirement
model.addConstr(
    BlueberryMinerals * BlueberryPacks + StrawberryMinerals * StrawberryPacks >= MinMinerals,
    name="mineral_requirement"
)

# Add strawberry-to-blueberry pack ratio constraint
model.addConstr(StrawberryPacks >= StrawberryBlueberryRatio * BlueberryPacks, name="strawberry_blueberry_ratio")

# Set objective
model.setObjective(BlueberrySugar * BlueberryPacks + StrawberrySugar * StrawberryPacks, gp.GRB.MINIMIZE)

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
