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
PatientsElectronic = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PatientsElectronic")
PatientsRegular = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PatientsRegular")

# Add non-negativity constraint for PatientsElectronic
model.addConstr(PatientsElectronic >= 0, name="non_negative_PatientsElectronic")

# Add non-negativity constraint for PatientsRegular
model.addConstr(PatientsRegular >= 0, name="non_negative_PatientsRegular")

# Add constraint to ensure the total time used for electronic thermometer readings does not exceed TotalTime
model.addConstr(PatientsElectronic * TimeElectronic <= TotalTime, name="total_time_constraint")

# Add constraint for total time used by regular thermometer readings
model.addConstr(PatientsRegular * TimeRegular <= TotalTime, name="total_time_regular")

# Add constraint to ensure at least RatioElectronicRegular times as many patients are checked by electronic thermometer compared to regular thermometer
model.addConstr(PatientsElectronic >= RatioElectronicRegular * PatientsRegular, name="electronic_vs_regular")

# Add the constraint to ensure the number of patients checked by the regular thermometer meets the minimum
model.addConstr(PatientsRegular >= MinPatientsRegular, name="min_patients_regular")

# Add total time constraint for using both thermometers
model.addConstr(
    PatientsElectronic * TimeElectronic + PatientsRegular * TimeRegular <= TotalTime,
    name="total_time_constraint"
)

# Add ratio constraint between patients checked by electronic and regular thermometers
model.addConstr(PatientsElectronic >= RatioElectronicRegular * PatientsRegular, name="ratio_constraint")

# Add constraint for minimum number of patients checked by the regular thermometer
model.addConstr(PatientsRegular >= MinPatientsRegular, name="min_patients_regular")

# Set objective
model.setObjective(PatientsElectronic + PatientsRegular, gp.GRB.MAXIMIZE)

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
