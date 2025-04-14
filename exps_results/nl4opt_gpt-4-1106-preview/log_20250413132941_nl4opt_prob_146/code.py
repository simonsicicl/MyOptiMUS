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
NumberOfBlueberryPacks = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfBlueberryPacks")
NumberOfStrawberryPacks = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfStrawberryPacks")

model.addConstr(NumberOfBlueberryPacks >= 0, name="non_negativity_blueberry_packs")

# Ensure the number of strawberry packs is non-negative
model.addConstr(NumberOfStrawberryPacks >= 0, name="strawberry_packs_non_negative")

# Add the constraint for minimum antioxidants from blueberries and strawberries
model.addConstr(BlueberryAntioxidants * NumberOfBlueberryPacks + StrawberryAntioxidants * NumberOfStrawberryPacks >= MinAntioxidants, name="min_antioxidants")

# Add constraint for minimum required minerals from blueberries and strawberries
model.addConstr(NumberOfBlueberryPacks * BlueberryMinerals + NumberOfStrawberryPacks * StrawberryMinerals >= MinMinerals, name="min_minerals")

# Add constraint: NumberOfStrawberryPacks >= 3 * NumberOfBlueberryPacks
model.addConstr(NumberOfStrawberryPacks >= 3 * NumberOfBlueberryPacks, name="strawberry_to_blueberry_ratio")

# Ensure the intake of anti-oxidants from blueberries and strawberries meets the minimum required units
model.addConstr(BlueberryAntioxidants * NumberOfBlueberryPacks + StrawberryAntioxidants * NumberOfStrawberryPacks >= MinAntioxidants, "min_antioxidants_requirement")

# Ensure the intake of minerals from blueberries and strawberries meets the minimum required units
model.addConstr(BlueberryMinerals * NumberOfBlueberryPacks + StrawberryMinerals * NumberOfStrawberryPacks >= MinMinerals, name="min_minerals_requirement")

# Maintain the ratio of packs of strawberries to blueberries
model.addConstr(NumberOfStrawberryPacks <= StrawberryBlueberryRatio * NumberOfBlueberryPacks, name="StrawberryBlueberryRatioConstraint")

# Define the objective function
model.setObjective(BlueberrySugar * NumberOfBlueberryPacks + StrawberrySugar * NumberOfStrawberryPacks, gp.GRB.MINIMIZE)

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
