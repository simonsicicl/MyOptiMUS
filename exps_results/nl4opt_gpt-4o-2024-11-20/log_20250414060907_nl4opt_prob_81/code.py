import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_81/data.json", "r") as f:
    data = json.load(f)

MotionDropsPerMinute = data["MotionDropsPerMinute"] # scalar parameter
MotionConsumption = data["MotionConsumption"] # scalar parameter
ManualDropsPerMinute = data["ManualDropsPerMinute"] # scalar parameter
ManualConsumption = data["ManualConsumption"] # scalar parameter
MaxManualFraction = data["MaxManualFraction"] # scalar parameter
MinMotionMachines = data["MinMotionMachines"] # scalar parameter
MinDropsPerMinute = data["MinDropsPerMinute"] # scalar parameter
MaxEnergyPerMinute = data["MaxEnergyPerMinute"] # scalar parameter
MotionMachines = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MotionMachines")
ManualMachines = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ManualMachines")

# No code needed: The variable "MotionMachines" is already constrained to be non-negative by default as it is defined as a continuous variable.

# No code needed - this constraint is implicitly enforced by the non-negative domain of the variable 'ManualMachines' due to its definition as a continuous variable in gurobi.

# Add constraint to enforce the maximum fraction of manual machines
model.addConstr((1 - MaxManualFraction) * ManualMachines <= MaxManualFraction * MotionMachines, name="manual_fraction_limit")

# Add constraint to ensure at least MinMotionMachines motion activated machines are purchased
model.addConstr(MotionMachines >= MinMotionMachines, name="min_motion_machines")

# Add minimum drops per minute constraint
model.addConstr(MotionDropsPerMinute * MotionMachines + ManualDropsPerMinute * ManualMachines >= MinDropsPerMinute, name="min_drops_per_minute")

# Add energy consumption constraint
model.addConstr(
    MotionConsumption * MotionMachines + ManualConsumption * ManualMachines <= MaxEnergyPerMinute,
    name="energy_consumption_limit"
)

# Add constraint for minimum total drops per minute  
model.addConstr(MotionDropsPerMinute * MotionMachines + ManualDropsPerMinute * ManualMachines >= MinDropsPerMinute, name="min_drops_per_minute")

# Add energy consumption constraint
model.addConstr(MotionConsumption * MotionMachines + ManualConsumption * ManualMachines <= MaxEnergyPerMinute, 
                name="energy_consumption_limit")

# Add constraint to ensure the fraction of manual machines does not exceed the maximum allowed
model.addConstr(ManualMachines <= MaxManualFraction * (MotionMachines + ManualMachines), name="manual_fraction_limit")

# Add constraint to ensure the minimum number of motion activated machines are purchased
model.addConstr(MotionMachines >= MinMotionMachines, name="min_motion_machines")

# Set objective
model.setObjective(MotionMachines + ManualMachines, gp.GRB.MINIMIZE)

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
