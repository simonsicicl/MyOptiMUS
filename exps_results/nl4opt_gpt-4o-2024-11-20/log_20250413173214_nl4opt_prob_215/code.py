import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_215/data.json", "r") as f:
    data = json.load(f)

InspectionTimeWashingMachine = data["InspectionTimeWashingMachine"] # scalar parameter
FixingTimeWashingMachine = data["FixingTimeWashingMachine"] # scalar parameter
InspectionTimeFreezer = data["InspectionTimeFreezer"] # scalar parameter
FixingTimeFreezer = data["FixingTimeFreezer"] # scalar parameter
TotalInspectionTime = data["TotalInspectionTime"] # scalar parameter
TotalFixingTime = data["TotalFixingTime"] # scalar parameter
EarningsWashingMachine = data["EarningsWashingMachine"] # scalar parameter
EarningsFreezer = data["EarningsFreezer"] # scalar parameter
NumWashingMachinesFixed = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumWashingMachinesFixed")
NumFreezersFixed = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumFreezersFixed")

# Add constraint to ensure the number of washing machines fixed is non-negative
model.addConstr(NumWashingMachinesFixed >= 0, name="non_negative_washing_machines_fixed")

# Ensure the number of freezers fixed is non-negative
model.addConstr(NumFreezersFixed >= 0, name="num_freezers_fixed_non_negative")

model.addConstr(
    NumWashingMachinesFixed * InspectionTimeWashingMachine + NumFreezersFixed * InspectionTimeFreezer <= TotalInspectionTime,
    name="total_inspection_time_constraint"
)

# Add total fixing time constraint
model.addConstr(
    NumWashingMachinesFixed * FixingTimeWashingMachine + NumFreezersFixed * FixingTimeFreezer <= TotalFixingTime,
    name="total_fixing_time_constraint"
)

# Add constraint on total available inspection time
model.addConstr(NumWashingMachinesFixed * InspectionTimeWashingMachine + NumFreezersFixed * InspectionTimeFreezer <= TotalInspectionTime, name="inspection_time_limit")

# Add constraint for total available fixing time
model.addConstr(
    NumWashingMachinesFixed * FixingTimeWashingMachine + NumFreezersFixed * FixingTimeFreezer <= TotalFixingTime,
    name="TotalFixingTimeConstraint"
)

# Set objective
model.setObjective(EarningsWashingMachine * NumWashingMachinesFixed + EarningsFreezer * NumFreezersFixed, gp.GRB.MAXIMIZE)

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
