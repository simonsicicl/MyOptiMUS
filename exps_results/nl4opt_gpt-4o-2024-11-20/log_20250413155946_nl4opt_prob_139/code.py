import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_139/data.json", "r") as f:
    data = json.load(f)

SpitTestTime = data["SpitTestTime"] # scalar parameter
SwabTestTime = data["SwabTestTime"] # scalar parameter
SpitSwabRatio = data["SpitSwabRatio"] # scalar parameter
MinSwabs = data["MinSwabs"] # scalar parameter
TotalTime = data["TotalTime"] # scalar parameter
NumberOfSpitTests = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfSpitTests")
NumberOfSwabTests = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfSwabTests")

# Add constraint to ensure total time spent on spit and swab tests does not exceed the available TotalTime
model.addConstr(NumberOfSpitTests * SpitTestTime + NumberOfSwabTests * SwabTestTime <= TotalTime, name="time_limit_constraint")

# Add constraint for minimum ratio of spit tests to swab tests
model.addConstr(NumberOfSpitTests >= SpitSwabRatio * NumberOfSwabTests, name="min_spit_to_swab_ratio")

# No code needed, as non-negativity is inherent to the variable type (GRB.CONTINUOUS); this constraint is automatically satisfied.

# The constraint is already defined inherently by the non-negative domain of the variable `NumberOfSwabTests`. No additional code is needed.

# Add constraint to ensure at least the minimum number of swab tests is conducted  
model.addConstr(NumberOfSwabTests >= MinSwabs, name="min_swab_tests_constraint")

# Add operational time constraint
model.addConstr(
    SpitTestTime * NumberOfSpitTests + SwabTestTime * NumberOfSwabTests <= TotalTime, 
    name="clinic_operational_time"
)

# Add constraint ensuring the number of spit tests is at least SpitSwabRatio times the number of swab tests
model.addConstr(NumberOfSpitTests >= SpitSwabRatio * NumberOfSwabTests, name="spit_swab_ratio")

# Add constraint to ensure the number of swab tests meets the minimum requirement
model.addConstr(NumberOfSwabTests >= MinSwabs, name="min_swab_tests")

# Set objective
model.setObjective(NumberOfSpitTests + NumberOfSwabTests, gp.GRB.MAXIMIZE)

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
