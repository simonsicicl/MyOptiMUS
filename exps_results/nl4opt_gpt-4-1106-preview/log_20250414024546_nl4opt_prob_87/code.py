import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_87/data.json", "r") as f:
    data = json.load(f)

SlicesPerMinuteManual = data["SlicesPerMinuteManual"] # scalar parameter
SlicesPerMinuteAutomatic = data["SlicesPerMinuteAutomatic"] # scalar parameter
GreasePerMinuteManual = data["GreasePerMinuteManual"] # scalar parameter
GreasePerMinuteAutomatic = data["GreasePerMinuteAutomatic"] # scalar parameter
MinTotalSlices = data["MinTotalSlices"] # scalar parameter
MaxTotalGrease = data["MaxTotalGrease"] # scalar parameter
NumManualSlicers = model.addVar(vtype=gp.GRB.INTEGER, name="NumManualSlicers")
NumAutomaticSlicers = model.addVar(vtype=gp.GRB.INTEGER, name="NumAutomaticSlicers")

# No code needed since the variable NumManualSlicers is already defined as an integer variable which implicitly cannot be negative.

# No code needed since the variable NumAutomaticSlicers is already defined to be an integer, 
# which inherently ensures it is non-negative in the addVar function.

# Constraint: Number of manual slicers must be less than or equal to the number of automatic slicers
model.addConstr(NumManualSlicers <= NumAutomaticSlicers, name="manual_less_equal_automatic")

# Add constraint for total slicing capacity to be at least MinTotalSlices slices per minute
model.addConstr(NumManualSlicers * SlicesPerMinuteManual + NumAutomaticSlicers * SlicesPerMinuteAutomatic >= MinTotalSlices, name="min_total_slices")

# Add total grease usage constraint
model.addConstr(NumManualSlicers * GreasePerMinuteManual + NumAutomaticSlicers * GreasePerMinuteAutomatic <= MaxTotalGrease, "TotalGreaseConstraint")

# Ensure the minimum total number of slices required per minute is met
model.addConstr(
    NumManualSlicers * SlicesPerMinuteManual + NumAutomaticSlicers * SlicesPerMinuteAutomatic >= MinTotalSlices,
    name="min_total_slices")

# Ensure the total units of grease used per minute do not exceed the maximum allowed
model.addConstr(NumManualSlicers * GreasePerMinuteManual + NumAutomaticSlicers * GreasePerMinuteAutomatic <= MaxTotalGrease, "max_grease_usage")

# Set objective
model.setObjective(NumManualSlicers + NumAutomaticSlicers, gp.GRB.MINIMIZE)

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
