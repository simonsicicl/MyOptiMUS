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
TimeOnAuto = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TimeOnAuto")
PatientsManual = model.addVar(vtype=gp.GRB.INTEGER, name="PatientsManual")
PatientsAuto = model.addVar(vtype=gp.GRB.INTEGER, name="PatientsAuto")

# Constraint to ensure the time on automatic machine is non-negative
model.addConstr(TimeOnAuto >= 0, name="time_on_auto_non_negative")

# Since there's no reference to a variable that needs to be defined or altered,
# no code is needed for this constraint. The constraint seems to be a reminder
# or a note rather than something that translates into a Gurobi constraint.

# Constraint: Total time on automatic and manual measurements must not exceed total clinic time
model.addConstr(TimeOnAuto + (PatientsManual * TManual) <= TotalTime, name="total_clinic_time")

# Ensure that at least RatioManualToAuto times as many patients are processed manually than automatically
model.addConstr(PatientsManual >= RatioManualToAuto * (TimeOnAuto / TAuto), name="ManualToAutoRatio")

# Add constraint to ensure at least MinPatientsAuto patients are processed automatically
model.addConstr(PatientsAuto >= MinPatientsAuto, name="min_patients_auto")

# Compute total time on manual machine
TimeOnManual = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TimeOnManual")
model.addConstr(TimeOnManual == PatientsManual * TManual, name="manual_machine_time")

# Constrain the minimum number of patients processed manually to be at least a certain ratio of the minimum for automatic machines
model.addConstr(PatientsManual >= RatioManualToAuto * MinPatientsAuto, name="min_ratio_manual_to_auto")

# Constraint: The total time spent on automatic machine measurements must not exceed the total operational time of the clinic
model.addConstr(TimeOnAuto <= TotalTime, name="auto_measurement_time")

# Constraint: Patients processed manually must be at least twice the number of patients processed automatically
model.addConstr(PatientsManual >= RatioManualToAuto * PatientsAuto, name="manual_to_auto_patient_ratio")

# Add minimum patients auto-processing constraint
model.addConstr(PatientsAuto >= MinPatientsAuto, name="min_patients_auto_processing")

# Add constraint for the total time on automatic measurements
model.addConstr(TimeOnAuto == TAuto * PatientsAuto, name="time_on_auto_constraint")

# Set objective
model.setObjective(PatientsManual + PatientsAuto, gp.GRB.MAXIMIZE)

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
