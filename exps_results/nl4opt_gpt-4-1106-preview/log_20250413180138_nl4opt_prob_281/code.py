import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_281/data.json", "r") as f:
    data = json.load(f)

CoconutOilTime = data["CoconutOilTime"] # scalar parameter
LavenderTime = data["LavenderTime"] # scalar parameter
MinCoconutOilUnits = data["MinCoconutOilUnits"] # scalar parameter
MaxCombinedUnits = data["MaxCombinedUnits"] # scalar parameter
MaxOilLavenderRatio = data["MaxOilLavenderRatio"] # scalar parameter
CoconutOilUnits = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CoconutOilUnits")
LavenderUnits = model.addVar(vtype=gp.GRB.CONTINUOUS, name="LavenderUnits")

# Add non-negativity constraint for coconut oil units
model.addConstr(CoconutOilUnits >= 0, name="coconut_oil_nonnegativity")

# Lavender units must be non-negative
model.addConstr(LavenderUnits >= 0, name="lavender_non_negative")

# Ensure that a minimum amount of coconut oil units is added to the body wash
model.addConstr(CoconutOilUnits >= MinCoconutOilUnits, name="min_coconut_oil")

# Add constraint for maximum combined units of coconut oil and lavender
model.addConstr(CoconutOilUnits + LavenderUnits <= MaxCombinedUnits, name="max_combined_units_constraint")

# Constraint: The ratio of CoconutOilUnits to LavenderUnits must not exceed MaxOilLavenderRatio
model.addConstr(CoconutOilUnits <= MaxOilLavenderRatio * LavenderUnits, "Ratio_CoconutOil_to_Lavender")

# Define the objective function
model.setObjective(CoconutOilUnits * CoconutOilTime + LavenderUnits * LavenderTime, gp.GRB.MINIMIZE)

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
