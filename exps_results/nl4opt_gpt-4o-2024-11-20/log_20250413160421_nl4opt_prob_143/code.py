import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_143/data.json", "r") as f:
    data = json.load(f)

TotalMedicinalUnits = data["TotalMedicinalUnits"] # scalar parameter
LargePillMedicinalUnits = data["LargePillMedicinalUnits"] # scalar parameter
LargePillFillerUnits = data["LargePillFillerUnits"] # scalar parameter
SmallPillMedicinalUnits = data["SmallPillMedicinalUnits"] # scalar parameter
SmallPillFillerUnits = data["SmallPillFillerUnits"] # scalar parameter
MinimumLargePills = data["MinimumLargePills"] # scalar parameter
MinimumSmallPillsPercentage = data["MinimumSmallPillsPercentage"] # scalar parameter
LargePills = model.addVar(vtype=gp.GRB.CONTINUOUS, name="LargePills")
SmallPills = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SmallPills")

# Add constraints for non-negativity and production limits for pills
model.addConstr(LargePills >= 0, name="non_negativity_large_pills")

model.addConstr(LargePills >= MinimumLargePills, name="min_production_large_pills")

model.addConstr((1 - MinimumSmallPillsPercentage) * SmallPills >= MinimumSmallPillsPercentage * LargePills, name="min_small_pills_percentage")

# No code is needed: Gurobi variables by default have non-negativity constraints unless explicitly set otherwise.

# Add constraint for total medicinal units
model.addConstr(
    LargePillMedicinalUnits * LargePills + SmallPillMedicinalUnits * SmallPills <= TotalMedicinalUnits,
    name="TotalMedicinalUnitsConstraint"
)

# Add constraint ensuring the number of large pills produced is at least the minimum
model.addConstr(LargePills >= MinimumLargePills, name="min_large_pills")

# Add constraint for MinimumSmallPillsPercentage
model.addConstr((1 - MinimumSmallPillsPercentage) * SmallPills >= MinimumSmallPillsPercentage * LargePills, 
                name="minimum_small_pills_percentage")

# Add constraint for minimum large pills production
model.addConstr(LargePills >= MinimumLargePills, name="min_large_pills")

# Add constraint to ensure the minimum percentage of total pills are small pills
model.addConstr((1 - MinimumSmallPillsPercentage) * SmallPills >= MinimumSmallPillsPercentage * LargePills, 
                name="min_small_pills_percentage")

# Add constraint to ensure total medicinal ingredients used do not exceed available stock
model.addConstr(
    LargePills * LargePillMedicinalUnits + SmallPills * SmallPillMedicinalUnits <= TotalMedicinalUnits,
    name="medicinal_ingredient_limit"
)

# Set objective
model.setObjective(LargePills * LargePillFillerUnits + SmallPills * SmallPillFillerUnits, gp.GRB.MINIMIZE)

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
