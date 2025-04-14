import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_257/data.json", "r") as f:
    data = json.load(f)

PlatinumPalladiumHeavy = data["PlatinumPalladiumHeavy"] # scalar parameter
PalladiumPalladiumHeavy = data["PalladiumPalladiumHeavy"] # scalar parameter
ConversionRatePalladiumHeavy = data["ConversionRatePalladiumHeavy"] # scalar parameter
PlatinumPlatinumHeavy = data["PlatinumPlatinumHeavy"] # scalar parameter
PalladiumPlatinumHeavy = data["PalladiumPlatinumHeavy"] # scalar parameter
ConversionRatePlatinumHeavy = data["ConversionRatePlatinumHeavy"] # scalar parameter
TotalPlatinum = data["TotalPlatinum"] # scalar parameter
TotalPalladium = data["TotalPalladium"] # scalar parameter
PalladiumHeavyCatalystUnits = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PalladiumHeavyCatalystUnits")
PlatinumHeavyCatalystUnits = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PlatinumHeavyCatalystUnits")

# Platinum usage for palladium-heavy catalysts is non-negative  
model.addConstr(PlatinumPalladiumHeavy * PalladiumHeavyCatalystUnits >= 0, name="non_negative_platinum_usage")

# No additional constraint needed as the non-negativity is inherently respected by the variable definition (gp.GRB.CONTINUOUS ensures the variable is non-negative by default)

# No code needed: The constraint \\( \textup{PlatinumHeavyCatalystUnits} \times \textup{PlatinumPlatinumHeavy} \geq 0 \\) is always satisfied since both \\( \textup{PlatinumHeavyCatalystUnits} \\) and \\( \textup{PlatinumPlatinumHeavy} \\) are non-negative by definition.

# No additional code is needed as the constraint is inherently satisfied.
# PalladiumPlatinumHeavy is a constant (14), and PlatinumHeavyCatalystUnits is a continuous variable initialized as non-negative in Gurobi by default.

# Add platinum utilization constraint
model.addConstr(
    PalladiumHeavyCatalystUnits * PlatinumPalladiumHeavy + PlatinumHeavyCatalystUnits * PlatinumPlatinumHeavy <= TotalPlatinum,
    name="platinum_utilization"
)

# Add constraint to ensure palladium usage does not exceed the available total palladium
model.addConstr(
    PalladiumHeavyCatalystUnits * PalladiumPalladiumHeavy + PlatinumHeavyCatalystUnits * PalladiumPlatinumHeavy <= TotalPalladium, 
    name="palladium_usage_limit"
)

# Add constraint for platinum consumption
model.addConstr(
    PlatinumPalladiumHeavy * PalladiumHeavyCatalystUnits + 
    PlatinumPlatinumHeavy * PlatinumHeavyCatalystUnits <= 
    TotalPlatinum, 
    name="platinum_consumption_limit"
)

# Add constraint to ensure palladium consumption does not exceed available palladium
model.addConstr(
    PalladiumPalladiumHeavy * PalladiumHeavyCatalystUnits + PalladiumPlatinumHeavy * PlatinumHeavyCatalystUnits <= TotalPalladium,
    name="palladium_limit"
)

# Set objective
model.setObjective(
    ConversionRatePalladiumHeavy * PalladiumHeavyCatalystUnits + ConversionRatePlatinumHeavy * PlatinumHeavyCatalystUnits,
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
