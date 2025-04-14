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
NumberOfTemperatureChecks = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfTemperatureChecks")
NumberOfBloodTests = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfBloodTests")

# Since NumberOfTemperatureChecks is already defined as a non-negative integer variable, no additional constraint is needed
# The non-negativity constraint is inherently applied through the variable definition in Gurobi

# Add non-negativity constraint for the number of blood tests
model.addConstr(NumberOfBloodTests >= 0, name="non_negativity_blood_tests")

# Add constraint for minimum number of blood tests
model.addConstr(NumberOfBloodTests >= MinBloodTests, name="min_blood_tests")

# Add constraint: Number of temperature checks must be at least TemperatureBloodTestFactor times the number of blood tests
model.addConstr(NumberOfTemperatureChecks >= TemperatureBloodTestFactor * NumberOfBloodTests, name="temp_checks_blood_tests")

# Define the constraint for total time spent on temperature checks and blood tests not exceeding total available staff time
model.addConstr(NumberOfTemperatureChecks * TemperatureCheckTime + NumberOfBloodTests * BloodTestTime <= TotalStaffTime, name="staff_time")

# Ensure the number of blood tests performed meets the minimum required
model.addConstr(NumberOfBloodTests >= MinBloodTests, name="min_blood_tests_requirement")

# Add constraint to ensure the time used by temperature checks and blood tests does not exceed staff time available
model.addConstr(NumberOfTemperatureChecks * TemperatureCheckTime + NumberOfBloodTests * BloodTestTime <= TotalStaffTime, name="time_constraint")

# Add constraint: Number of temperature checks must be at least a factor times more than the number of blood tests
model.addConstr(NumberOfTemperatureChecks >= TemperatureBloodTestFactor * NumberOfBloodTests, name="temp_checks_to_blood_tests")

# Constraint: Total time for all temperature checks and blood tests must not exceed the total available staff time
model.addConstr(TemperatureCheckTime * NumberOfTemperatureChecks + BloodTestTime * NumberOfBloodTests <= TotalStaffTime, name="staff_time_limit")

# Add constraint for the minimum number of blood tests
model.addConstr(NumberOfBloodTests >= MinBloodTests, name="min_blood_tests_constraint")

# Ensure the number of temperature checks is at least TemperatureBloodTestFactor times higher than the number of blood tests
model.addConstr(NumberOfTemperatureChecks >= TemperatureBloodTestFactor * NumberOfBloodTests, "temp_checks_to_blood_tests")

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
