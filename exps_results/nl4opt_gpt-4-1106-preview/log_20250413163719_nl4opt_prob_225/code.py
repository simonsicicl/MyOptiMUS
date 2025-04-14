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
NumberWidePipes = model.addVar(vtype=gp.GRB.INTEGER, name="NumberWidePipes")
NumberNarrowPipes = model.addVar(vtype=gp.GRB.INTEGER, name="NumberNarrowPipes")

# Add constraint to ensure the number of wide pipes is non-negative
model.addConstr(NumberWidePipes >= 0, name="non_negative_wide_pipes")

# Since NumberNarrowPipes is already ensured to be an integer variable, adding the non-negative constraint
model.addConstr(NumberNarrowPipes >= 0, name="non_negativity_NumberNarrowPipes")

# Add constraint for the ratio of wide to narrow pipes
model.addConstr(NumberWidePipes <= MaxWideToNarrowRatio * NumberNarrowPipes, "wide_to_narrow_ratio")

# Add water transportation capacity constraint
model.addConstr(NumberWidePipes * WidePipeCapacity + NumberNarrowPipes * NarrowPipeCapacity >= MinTotalWater, name="min_total_water")

# Add constraint for the minimum number of wide pipes
model.addConstr(NumberWidePipes >= MinWidePipes, name="min_wide_pipes")

# Ensure that the number of wide pipes does not exceed 0.33 times the number of narrow pipes
model.addConstr(NumberWidePipes <= MaxWideToNarrowRatio * NumberNarrowPipes, name="wide_to_narrow_pipe_ratio")

# Ensure that the minimum total amount of water is transported
model.addConstr(NumberWidePipes * WidePipeCapacity + NumberNarrowPipes * NarrowPipeCapacity >= MinTotalWater, name="min_total_water_constraint")

# Ensure that at least the minimum number of wide pipes are used
model.addConstr(NumberWidePipes >= MinWidePipes, name="min_wide_pipes_constraint")

# Define objective function
model.setObjective(NumberWidePipes + NumberNarrowPipes, gp.GRB.MINIMIZE)

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
