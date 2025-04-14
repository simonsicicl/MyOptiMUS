import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_109/data.json", "r") as f:
    data = json.load(f)

TAuto = data["TAuto"] # scalar parameter
TManual = data["TManual"] # scalar parameter
RatioManualToAuto = data["RatioManualToAuto"] # scalar parameter
MinPatientsAuto = data["MinPatientsAuto"] # scalar parameter
TotalTime = data["TotalTime"] # scalar parameter
PatientsAuto = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PatientsAuto")
TimeAuto = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TimeAuto")
TimeManual = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TimeManual")
PatientsManual = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PatientsManual")

# Adding constraint: The time spent on automatic machine measurements must be non-negative
model.addConstr(TimeAuto >= 0, name="non_negative_constraint_TimeAuto")

# No additional code needed since the variable "TimeManual" is already non-negative due to its default lower bound (0) in Gurobi.

# Add total operational time constraint
model.addConstr(TimeAuto + TimeManual <= TotalTime, name="total_operational_time")

# Add constraint to ensure at least RatioManualToAuto times as many patients are processed manually than automatically
model.addConstr(PatientsManual >= RatioManualToAuto * PatientsAuto, name="manual_to_auto_ratio")

# Add the constraint to ensure at least MinPatientsAuto patients are processed using the automatic machine
model.addConstr(PatientsAuto >= MinPatientsAuto, name="min_patients_auto")

# Add constraint to ensure total time spent on automatic measurements equals patients processed multiplied by time per patient
model.addConstr(TimeAuto == PatientsAuto * TAuto, name="time_auto_constraint")

# Add constraint to compute TimeAuto based on PatientsAuto and TAuto
model.addConstr(TimeAuto == TAuto * PatientsAuto, name="TimeAuto_calculation")

# Add constraint to compute TimeManual based on PatientsManual and TManual
model.addConstr(TimeManual == TManual * PatientsManual, name="TimeManual_calculation")

# Add constraint to ensure total processing time does not exceed clinic's operational time
model.addConstr(
    PatientsAuto * TAuto + PatientsManual * TManual <= TotalTime, 
    name="processing_time_limit"
)

# Add constraint to ensure the number of patients processed by the automatic machine meets the minimum threshold
model.addConstr(PatientsAuto >= MinPatientsAuto, name="min_patients_auto")

# Add constraint to ensure patients processed by the manual machine 
# are at least the prescribed multiple of those processed by the automatic machine
model.addConstr(PatientsManual >= RatioManualToAuto * PatientsAuto, name="manual_to_auto_ratio")

# Set objective
model.setObjective(PatientsAuto + PatientsManual, gp.GRB.MAXIMIZE)

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
