import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_176/data.json", "r") as f:
    data = json.load(f)

SmallJarVolume = data["SmallJarVolume"] # scalar parameter
LargeJarVolume = data["LargeJarVolume"] # scalar parameter
MinimumVolume = data["MinimumVolume"] # scalar parameter
LargeJars = model.addVar(vtype=gp.GRB.INTEGER, name="LargeJars")
SmallJars = model.addVar(vtype=gp.GRB.INTEGER, name="SmallJars")

model.addConstr(LargeJars >= 0, name="large_jars_non_negative")

model.addConstr(SmallJars >= 0, name="small_jars_non_negative")

# Ensure the number of large jars does not exceed the number of small jars
model.addConstr(LargeJars <= SmallJars, name="large_jars_leq_small_jars")

# Add constraint to ensure the total volume of jam meets the minimum required volume
model.addConstr(SmallJarVolume * SmallJars + LargeJarVolume * LargeJars >= MinimumVolume, name="min_total_volume")

# Ensure that the total volume of jam shipped meets or exceeds the minimum requirement
model.addConstr(SmallJarVolume * SmallJars + LargeJarVolume * LargeJars >= MinimumVolume, name="MinimumVolumeRequirement")

# Define objective function
model.setObjective(LargeJars + SmallJars, gp.GRB.MINIMIZE)

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
