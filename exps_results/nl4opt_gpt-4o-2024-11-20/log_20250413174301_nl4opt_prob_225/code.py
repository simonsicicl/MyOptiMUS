import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_225/data.json", "r") as f:
    data = json.load(f)

WidePipeCapacity = data["WidePipeCapacity"] # scalar parameter
NarrowPipeCapacity = data["NarrowPipeCapacity"] # scalar parameter
MaxWideToNarrowRatio = data["MaxWideToNarrowRatio"] # scalar parameter
MinTotalWater = data["MinTotalWater"] # scalar parameter
MinWidePipes = data["MinWidePipes"] # scalar parameter
WidePipes = model.addVar(vtype=gp.GRB.CONTINUOUS, name="WidePipes")
NarrowPipes = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NarrowPipes")

# No additional code is necessary as the non-negativity of the WidePipes variable is implicitly enforced by its domain (continuous variables in Gurobi are non-negative by default).

# The non-negativity of narrow pipes is automatically handled by Gurobi's non-negative domain for continuous variables.

# Add constraint: WidePipes <= MaxWideToNarrowRatio * NarrowPipes
model.addConstr(WidePipes <= MaxWideToNarrowRatio * NarrowPipes, name="wide_to_narrow_ratio")

# Add constraint to ensure total water transported per minute meets the minimum required
model.addConstr(
    WidePipes * WidePipeCapacity + NarrowPipes * NarrowPipeCapacity >= MinTotalWater,
    name="min_water_transport"
)

# Add constraint to ensure the number of wide pipes used is at least MinWidePipes
model.addConstr(WidePipes >= MinWidePipes, name="min_wide_pipes")

# Add constraint to ensure the number of wide pipes meets the minimum requirement
model.addConstr(WidePipes >= MinWidePipes, name="min_wide_pipes")

# Add constraint on the maximum allowable fraction of wide pipes relative to narrow pipes
model.addConstr(WidePipes <= MaxWideToNarrowRatio * NarrowPipes, name="wide_to_narrow_ratio")

# Add constraint to ensure the total water transported meets the minimum required amount
model.addConstr(WidePipes * WidePipeCapacity + NarrowPipes * NarrowPipeCapacity >= MinTotalWater, name="min_water_transport")

# Add constraint to ensure the number of wide pipes does not exceed the maximum allowed ratio of narrow pipes
model.addConstr(WidePipes <= MaxWideToNarrowRatio * NarrowPipes, name="wide_to_narrow_pipe_ratio")

# Add constraint to ensure at least the minimum number of wide pipes is used
model.addConstr(WidePipes >= MinWidePipes, name="min_wide_pipes_constraint")

# Set objective
model.setObjective(WidePipes + NarrowPipes, gp.GRB.MINIMIZE)

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
