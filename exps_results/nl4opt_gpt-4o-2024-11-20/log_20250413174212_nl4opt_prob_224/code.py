import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_224/data.json", "r") as f:
    data = json.load(f)

TemperatureCheckTime = data["TemperatureCheckTime"] # scalar parameter
BloodTestTime = data["BloodTestTime"] # scalar parameter
MinBloodTests = data["MinBloodTests"] # scalar parameter
TemperatureBloodTestFactor = data["TemperatureBloodTestFactor"] # scalar parameter
TotalStaffTime = data["TotalStaffTime"] # scalar parameter
NumberOfTemperatureChecks = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfTemperatureChecks")
NumberOfBloodTests = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfBloodTests")

# The variable "NumberOfTemperatureChecks" is non-negative by default (continuous variables in Gurobi are non-negative), so no additional constraint is needed.

# The variable "NumberOfBloodTests" is non-negative due to its default lower bound (0) in Gurobi's `addVar`.

# Add minimum blood test constraint
model.addConstr(NumberOfBloodTests >= MinBloodTests, name="min_blood_tests")

# Add constraint for temperature checks being at least TemperatureBloodTestFactor times the number of blood tests
model.addConstr(NumberOfTemperatureChecks >= TemperatureBloodTestFactor * NumberOfBloodTests, name="temp_check_vs_blood_test")

# Add constraint for total staff time
model.addConstr(
    NumberOfTemperatureChecks * TemperatureCheckTime + NumberOfBloodTests * BloodTestTime <= TotalStaffTime,
    name="TotalStaffTimeConstraint"
)

# Add constraint for total time spent on temperature checks and blood tests
model.addConstr(
    TemperatureCheckTime * NumberOfTemperatureChecks + BloodTestTime * NumberOfBloodTests <= TotalStaffTime,
    name="total_staff_time_constraint"
)

# Add constraint to enforce minimum required number of blood tests
model.addConstr(NumberOfBloodTests >= MinBloodTests, name="min_blood_tests_constraint")

# Add constraint ensuring temperature checks are at least TemperatureBloodTestFactor times the blood tests
model.addConstr(NumberOfTemperatureChecks >= TemperatureBloodTestFactor * NumberOfBloodTests, name="min_temperature_checks")

# Set objective
model.setObjective(NumberOfTemperatureChecks + NumberOfBloodTests, gp.GRB.MAXIMIZE)

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
