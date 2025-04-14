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
NumberManualSlicers = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberManualSlicers")
NumberAutomaticSlicers = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberAutomaticSlicers")

# Since the variable "NumberManualSlicers" is already defined with non-negativity enforced as it is declared as a continuous variable (default lower bound is 0), no additional code is needed for this constraint.

# No additional code needed since the variable 'NumberAutomaticSlicers' domain already ensures non-negativity due to its default lower bound of 0.

# Add constraint: Number of manual slicers must be less than the number of automatic slicers
model.addConstr(NumberManualSlicers <= NumberAutomaticSlicers - 1, name="manual_vs_automatic_slicers")

# Add constraint for minimum required slicing capacity
model.addConstr(
    SlicesPerMinuteManual * NumberManualSlicers + SlicesPerMinuteAutomatic * NumberAutomaticSlicers >= MinTotalSlices, 
    name="min_slicing_capacity"
)

# Add grease usage constraint
model.addConstr(
    NumberManualSlicers * GreasePerMinuteManual + NumberAutomaticSlicers * GreasePerMinuteAutomatic <= MaxTotalGrease,
    name="grease_usage_constraint"
)

# Add constraint to ensure total slicing capacity meets the minimum required slicing rate
model.addConstr(
    NumberManualSlicers * SlicesPerMinuteManual + NumberAutomaticSlicers * SlicesPerMinuteAutomatic >= MinTotalSlices,
    name="slicing_capacity_constraint"
)

# Add constraint for grease usage of slicers per minute
model.addConstr(
    GreasePerMinuteManual * NumberManualSlicers + GreasePerMinuteAutomatic * NumberAutomaticSlicers <= MaxTotalGrease,
    name="grease_usage_limit"
)

# Set objective
model.setObjective(NumberManualSlicers + NumberAutomaticSlicers, gp.GRB.MINIMIZE)

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
