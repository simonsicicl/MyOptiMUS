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
NumberOfWashingMachinesFixed = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfWashingMachinesFixed")
NumberOfFreezersFixed = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfFreezersFixed")

# Since the variable NumberOfWashingMachinesFixed is already non-negative due to being integer type and there's no specific lower bound provided other than non-negativity, no additional constraint is needed.

# No code needed as the variable NumberOfFreezersFixed is already non-negative by definition
# Setting a variable to be of INTEGER type in Gurobi ensures it's non-negative by default

# Add constraint for the total inspection time
model.addConstr(InspectionTimeWashingMachine * NumberOfWashingMachinesFixed + InspectionTimeFreezer * NumberOfFreezersFixed <= TotalInspectionTime, "total_inspection_time")

# Add total fixing time constraint
model.addConstr(
    (FixingTimeWashingMachine * NumberOfWashingMachinesFixed) + 
    (FixingTimeFreezer * NumberOfFreezersFixed) <= 
    TotalFixingTime, 
    name="total_fixing_time"
)

# Total inspection time constraint
model.addConstr(InspectionTimeWashingMachine * NumberOfWashingMachinesFixed + InspectionTimeFreezer * NumberOfFreezersFixed <= TotalInspectionTime, "total_inspection_time")

# Add constraint for the total fixing time for washing machines and freezers
model.addConstr(FixingTimeWashingMachine * NumberOfWashingMachinesFixed + FixingTimeFreezer * NumberOfFreezersFixed <= TotalFixingTime, name="total_fixing_time")

# Define the objective function
model.setObjective(EarningsWashingMachine * NumberOfWashingMachinesFixed + EarningsFreezer * NumberOfFreezersFixed, gp.GRB.MAXIMIZE)

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
