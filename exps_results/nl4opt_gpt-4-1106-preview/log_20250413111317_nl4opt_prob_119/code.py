import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_119/data.json", "r") as f:
    data = json.load(f)

TimeElectronic = data["TimeElectronic"] # scalar parameter
TimeRegular = data["TimeRegular"] # scalar parameter
RatioElectronicRegular = data["RatioElectronicRegular"] # scalar parameter
MinPatientsRegular = data["MinPatientsRegular"] # scalar parameter
TotalTime = data["TotalTime"] # scalar parameter
PatientsCheckedElectronic = model.addVar(vtype=gp.GRB.INTEGER, name="PatientsCheckedElectronic")
PatientsCheckedRegular = model.addVar(vtype=gp.GRB.INTEGER, name="PatientsCheckedRegular")

model.addConstr(PatientsCheckedElectronic >= 0, "PatientsCheckedElectronic_non_negative")

model.addConstr(PatientsCheckedRegular >= 0, "PatientsCheckedNonNeg")

# Add constraint for total time used by electronic thermometer
model.addConstr(PatientsCheckedElectronic * TimeElectronic <= TotalTime, name="electronic_thermometer_time_limit")

# Time used for regular thermometer readings is at most TotalTime
time_used_constraint = model.addConstr(PatientsCheckedRegular * TimeRegular <= TotalTime, name="time_used_regular")

PatientsCheckedElectronic = model.addVar(vtype=gp.GRB.INTEGER, name='PatientsCheckedElectronic')
PatientsCheckedRegular = model.addVar(vtype=gp.GRB.INTEGER, name='PatientsCheckedRegular')

# At least a certain number of patients should be checked by the regular thermometer
model.addConstr(PatientsCheckedRegular >= MinPatientsRegular, "min_patients_regular_constraint")

# Ensure that the total time used for checking patients with both thermometers does not exceed the TotalTime
model.addConstr(TimeElectronic * PatientsCheckedElectronic + TimeRegular * PatientsCheckedRegular <= TotalTime, name="total_checking_time")

# Ensure that the ratio of the number of patients checked by the electronic thermometer to those checked by the regular thermometer is at least the minimum required
model.addConstr(PatientsCheckedElectronic >= RatioElectronicRegular * PatientsCheckedRegular, name="ratio_electronic_regular")

# Ensure that the minimum number of patients checked by the regular thermometer is satisfied
model.addConstr(PatientsCheckedRegular >= MinPatientsRegular, name="min_patients_checked_regular")

# Set objective
model.setObjective(PatientsCheckedElectronic + PatientsCheckedRegular, gp.GRB.MAXIMIZE)

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
