import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_135/data.json", "r") as f:
    data = json.load(f)

SulfateTime = data["SulfateTime"] # scalar parameter
GingerTime = data["GingerTime"] # scalar parameter
MinSulfate = data["MinSulfate"] # scalar parameter
TotalUnits = data["TotalUnits"] # scalar parameter
MaxSulfateGingerRatio = data["MaxSulfateGingerRatio"] # scalar parameter
SulfateUnits = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SulfateUnits")
GingerUnits = model.addVar(vtype=gp.GRB.CONTINUOUS, name="GingerUnits")

# Add constraint to ensure sulfate units meet minimum requirement
model.addConstr(SulfateUnits >= MinSulfate, name="min_sulfate_requirement")

# Add constraint to ensure the total units of sulfate and ginger equal the total required units
model.addConstr(SulfateUnits + GingerUnits == TotalUnits, name="total_units_constraint")

# Add sulfate-to-ginger ratio constraint
model.addConstr(SulfateUnits <= MaxSulfateGingerRatio * GingerUnits, name="sulfate_to_ginger_ratio")

# As the non-negativity constraint is already implied by the variable type (CONTINUOUS), no additional code is needed.

# Since the variable GingerUnits was already defined with a lower bound of 0 (default in gurobipy), no additional constraint is required.

# Add constraint ensuring the number of sulfate units meets the minimum requirement
model.addConstr(SulfateUnits >= MinSulfate, name="min_sulfate_requirement")

# Add constraint ensuring total units of sulfate and ginger equal required total units
model.addConstr(SulfateUnits + GingerUnits == TotalUnits, name="total_units_constraint")

# Add constraint to enforce the sulfate-to-ginger ratio
model.addConstr(SulfateUnits <= MaxSulfateGingerRatio * GingerUnits, name="sulfate_ginger_ratio")

# Add non-negativity constraints for SulfateUnits and GingerUnits
model.addConstr(SulfateUnits >= 0, name="non_negativity_sulfate")
model.addConstr(GingerUnits >= 0, name="non_negativity_ginger")

# Set objective
model.setObjective(SulfateTime * SulfateUnits + GingerTime * GingerUnits, gp.GRB.MINIMIZE)

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
