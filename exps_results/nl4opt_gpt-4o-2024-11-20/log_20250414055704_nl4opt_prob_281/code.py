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

# No code needed, as non-negativity is inherent for continuous variables in Gurobi.

# Lavender units must be non-negative
model.addConstr(LavenderUnits >= 0, name="non_negativity_LavenderUnits")

# Add constraint to enforce minimum units of coconut oil
model.addConstr(CoconutOilUnits >= MinCoconutOilUnits, name="min_coconut_oil")

# Add constraint: The total units of coconut oil and lavender combined cannot exceed MaxCombinedUnits
model.addConstr(CoconutOilUnits + LavenderUnits <= MaxCombinedUnits, name="combined_units_constraint")

# Add constraint for the coconut oil to lavender ratio
model.addConstr(CoconutOilUnits <= MaxOilLavenderRatio * LavenderUnits, name="coconut_to_lavender_ratio")

# Add minimum required units of coconut oil constraint  
model.addConstr(CoconutOilUnits >= MinCoconutOilUnits, name="min_coconut_oil_units")

# Add constraint for maximum combined units of coconut oil and lavender
model.addConstr(CoconutOilUnits + LavenderUnits <= MaxCombinedUnits, name="max_combined_units")

# Add constraint for the maximum allowed ratio of coconut oil to lavender
model.addConstr(CoconutOilUnits <= MaxOilLavenderRatio * LavenderUnits, name="max_coconut_oil_to_lavender_ratio")

# Add constraint for minimum requirement on coconut oil units
model.addConstr(CoconutOilUnits >= MinCoconutOilUnits, name="min_coconut_oil_requirement")

# Add constraint to limit the combined units of CoconutOilUnits and LavenderUnits
model.addConstr(CoconutOilUnits + LavenderUnits <= MaxCombinedUnits, name="combined_units_limit")

# Add constraint to ensure CoconutOilUnits does not exceed the maximum allowable ratio to LavenderUnits
model.addConstr(CoconutOilUnits <= MaxOilLavenderRatio * LavenderUnits, name="coconut_oil_to_lavender_ratio")

# Set objective
model.setObjective(CoconutOilTime * CoconutOilUnits + LavenderTime * LavenderUnits, gp.GRB.MINIMIZE)

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
