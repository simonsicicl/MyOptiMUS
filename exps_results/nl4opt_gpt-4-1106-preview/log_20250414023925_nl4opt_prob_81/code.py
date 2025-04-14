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
NumberOfMotionActivatedMachines = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfMotionActivatedMachines")
NumberOfManualMachines = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfManualMachines")

# No code needed since the variable NumberOfMotionActivatedMachines is already defined as an integer, which implicitly enforces non-negativity

# Constraint: The number of manual machines is non-negative
model.addConstr(NumberOfManualMachines >= 0, name="non_negativity_ManualMachines")

# Add constraint: At most MaxManualFraction of the total machines can be manual
model.addConstr(NumberOfManualMachines <= MaxManualFraction * (NumberOfMotionActivatedMachines + NumberOfManualMachines), "MaxManualMachinesConstraint")

# Ensure at least MinMotionMachines are motion activated
model.addConstr(NumberOfMotionActivatedMachines >= MinMotionMachines, name="min_motion_machines")

# Add constraint for minimum drops per minute required by the mall
model.addConstr(
    NumberOfMotionActivatedMachines * MotionDropsPerMinute + NumberOfManualMachines * ManualDropsPerMinute >= MinDropsPerMinute,
    name="min_drops_per_minute"
)

# Add constraint for maximum energy consumption per minute
model.addConstr(
    (NumberOfMotionActivatedMachines * MotionConsumption +
     NumberOfManualMachines * ManualConsumption) <= MaxEnergyPerMinute,
    name="max_energy_consumption"
)

# Add constraint to meet minimum drops per minute requirement from all machines
model.addConstr(NumberOfMotionActivatedMachines * MotionDropsPerMinute + NumberOfManualMachines * ManualDropsPerMinute >= MinDropsPerMinute, "min_drops_per_minute")

# Energy consumption constraint
energy_consumption_constraint = NumberOfMotionActivatedMachines * MotionConsumption + NumberOfManualMachines * ManualConsumption
model.addConstr(energy_consumption_constraint <= MaxEnergyPerMinute, name="Max_Energy_Consumption_Per_Minute")

# The number of manual machines cannot exceed the maximum fraction allowed of the total machines
model.addConstr(NumberOfManualMachines <= MaxManualFraction * (NumberOfMotionActivatedMachines + NumberOfManualMachines), name="max_manual_machines_fraction")

# Constraint: Number of motion activated machines must meet at least the minimum required
model.addConstr(NumberOfMotionActivatedMachines >= MinMotionMachines, name="min_motion_activated_machines")

# Set objective
model.setObjective(NumberOfMotionActivatedMachines + NumberOfManualMachines, gp.GRB.MINIMIZE)

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
