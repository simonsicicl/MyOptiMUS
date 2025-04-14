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
LargeJars = model.addVar(vtype=gp.GRB.CONTINUOUS, name="LargeJars")
SmallJars = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SmallJars")

# The variable "LargeJars" already has a non-negative domain by default since it is defined as a non-negative continuous variable.

# The variable SmallJars is already defined as non-negative due to its default properties in gurobipy (lower bound of 0).

# Add constraint ensuring the number of large jars does not exceed the number of small jars
model.addConstr(LargeJars <= SmallJars, name="large_small_jar_balance")

# Add constraint to ensure total jam volume in jars meets or exceeds the minimum volume requirement
model.addConstr(SmallJars * SmallJarVolume + LargeJars * LargeJarVolume >= MinimumVolume, name="minimum_jam_volume")

# Add total volume constraint for small and large jars
model.addConstr(SmallJarVolume * SmallJars + LargeJarVolume * LargeJars >= MinimumVolume, name="total_volume_constraint")

# Set objective
model.setObjective(SmallJars + LargeJars, gp.GRB.MINIMIZE)

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
