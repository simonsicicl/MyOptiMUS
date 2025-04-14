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
PlatinumUsedPalladiumHeavyCatalysts = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PlatinumUsedPalladiumHeavyCatalysts")
PlatinumUsedPlatinumHeavyCatalysts = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PlatinumUsedPlatinumHeavyCatalysts")
PalladiumUsedPlatinumHeavyCatalysts = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PalladiumUsedPlatinumHeavyCatalysts")
PalladiumUsedPalladiumHeavyCatalysts = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PalladiumUsedPalladiumHeavyCatalysts")

# Since the constraint is a non-negativity constraint and the variable is defined as continuous, no additional constraint is necessary because Gurobi's default lower bound for continuous variables is 0.
# If the constraint was explicitly needed, or if the default behavior of Gurobi was overridden:
model.addConstr(PlatinumUsedPalladiumHeavyCatalysts * PlatinumPalladiumHeavy >= 0, name="nonnegativity_platinum_palladium_heavy")

# Palladium used for palladium-heavy catalysts must be non-negative
model.addConstr(PalladiumUsedPalladiumHeavyCatalysts >= 0, name="PalladiumUsedPalladiumHeavyCatalysts_nonnegativity")

# The constraint ensures that the variable PlatinumUsedPlatinumHeavyCatalysts is non-negative
model.addConstr(PlatinumUsedPlatinumHeavyCatalysts >= 0, name="PlatinumUsedPlatinumHeavyCatalysts_nonnegativity")

# Since the variable is already defined as continuous and no constraints are needed beyond variable definition, no code is required.
# The non-negativity is ensured by the variable type (CONTINUOUS) in Gurobi, which defaults to non-negative.

# Add constraint for platinum usage in catalysts
model.addConstr(PlatinumUsedPalladiumHeavyCatalysts * PlatinumPalladiumHeavy +
                PlatinumUsedPlatinumHeavyCatalysts * PlatinumPlatinumHeavy <= TotalPlatinum,
                name="platinum_usage")

# Add constraint for total palladium used
model.addConstr(PalladiumUsedPalladiumHeavyCatalysts + PalladiumUsedPlatinumHeavyCatalysts <= TotalPalladium, name="total_palladium_limit")

# Constraint: Total palladium used is equal to the number of palladium-heavy catalysts produced times the units of palladium needed per catalyst.
model.addConstr(PalladiumUsedPalladiumHeavyCatalysts == PlatinumUsedPalladiumHeavyCatalysts * PalladiumPalladiumHeavy, "PalladiumUsedPalladiumHeavyCatalysts_total")

# No new auxiliary constraint needed for the total palladium consumption in platinum-heavy catalysts

# Ensure the total platinum used does not exceed the total available units of platinum
model.addConstr(PlatinumPalladiumHeavy * PlatinumUsedPalladiumHeavyCatalysts + PlatinumPlatinumHeavy * PlatinumUsedPlatinumHeavyCatalysts <= TotalPlatinum, "platinum_availability")

# Ensure the total palladium used does not exceed the total available units of palladium
model.addConstr(PalladiumPalladiumHeavy * PlatinumUsedPalladiumHeavyCatalysts + PalladiumPlatinumHeavy * PlatinumUsedPlatinumHeavyCatalysts <= TotalPalladium, name="palladium_usage_constraint")

# Set objective function
model.setObjective(ConversionRatePalladiumHeavy * PlatinumUsedPalladiumHeavyCatalysts +
                   ConversionRatePlatinumHeavy * PlatinumUsedPlatinumHeavyCatalysts, gp.GRB.MAXIMIZE)

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
