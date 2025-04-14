import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_124/data.json", "r") as f:
    data = json.load(f)

MgGummy = data["MgGummy"] # scalar parameter
ZnGummy = data["ZnGummy"] # scalar parameter
MgPill = data["MgPill"] # scalar parameter
ZnPill = data["ZnPill"] # scalar parameter
MinPills = data["MinPills"] # scalar parameter
GummyPillRatio = data["GummyPillRatio"] # scalar parameter
MaxMg = data["MaxMg"] # scalar parameter
GummyCount = model.addVar(vtype=gp.GRB.CONTINUOUS, name="GummyCount")
PillCount = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PillCount")

# No additional code needed since GummyCount is already defined as a non-negative continuous variable

# Add non-negativity constraint for the number of pills consumed
model.addConstr(PillCount >= 0, name="non_negative_pillcount")

# Add constraint to ensure the boy takes at least the minimum number of pills
model.addConstr(PillCount >= MinPills, name="min_pills_constraint")

# Add constraint: GummyCount must be at least GummyPillRatio times PillCount
model.addConstr(GummyCount >= GummyPillRatio * PillCount, name="min_gummy_ratio")

# Add constraint to limit the combined magnesium from gummies and pills
model.addConstr(
    (MgGummy * GummyCount) + (MgPill * PillCount) <= MaxMg, 
    name="magnesium_limit"
)

# Add minimum pills constraint
model.addConstr(PillCount >= MinPills, name="min_pills_constraint")

# Add constraint to maintain the gummies-to-pills ratio
model.addConstr(GummyCount >= GummyPillRatio * PillCount, name="gummies_to_pills_ratio")

# Add constraint to ensure total magnesium intake does not exceed the maximum allowable magnesium
model.addConstr(MgGummy * GummyCount + MgPill * PillCount <= MaxMg, name="max_magnesium_intake")

# Set objective
model.setObjective(ZnGummy * GummyCount + ZnPill * PillCount, gp.GRB.MAXIMIZE)

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
