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

# Ensure the amount of sulfate meets the minimum required units
model.addConstr(SulfateUnits >= MinSulfate, "min_sulfate_requirement")

# Add constraint for the total units of sulfate and ginger
model.addConstr(SulfateUnits + GingerUnits == TotalUnits, name="total_units")

model.addConstr((SulfateUnits <= MaxSulfateGingerRatio * (GingerUnits + 1e-6)), name="sulfate_ginger_ratio_constraint")

SulfateUnits = model.addVar(vtype=gp.GRB.CONTINUOUS, name='SulfateUnits')

# Since GingerUnits is already a non-negative continuous variable by default, no constraint is needed
# Guropy automatically assumes variables are non-negative unless otherwise specified

model.addConstr(GingerUnits >= 0, name="non_negativity_ginger")

# Total units of sulfate and ginger must equal the total required units of ingredients
model.addConstr(SulfateUnits + GingerUnits == TotalUnits, name="total_units")

# Add constraint to ensure the minimum required units of sulfate are satisfied
model.addConstr(SulfateUnits >= MinSulfate, name="min_sulfate_requirement")

# Constraint: The ratio of sulfate to ginger should not exceed the maximum ratio
model.addConstr(SulfateUnits <= GingerUnits * MaxSulfateGingerRatio, name="sulfate_ginger_ratio_constraint")

# Define the objective function
model.setObjective(SulfateUnits * SulfateTime + GingerUnits * GingerTime, gp.GRB.MINIMIZE)

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
