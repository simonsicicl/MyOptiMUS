import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_263/data.json", "r") as f:
    data = json.load(f)

BloodTestTime = data["BloodTestTime"] # scalar parameter
EarTestTime = data["EarTestTime"] # scalar parameter
BloodEarRatio = data["BloodEarRatio"] # scalar parameter
MinEarTests = data["MinEarTests"] # scalar parameter
TotalTime = data["TotalTime"] # scalar parameter
TotalBloodTestTime = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalBloodTestTime")
TotalEarTestTime = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalEarTestTime")
NumberEarTests = model.addVar(vtype=gp.GRB.INTEGER, name="NumberEarTests")
NumberBloodTests = model.addVar(vtype=gp.GRB.INTEGER, name="NumberBloodTests")

# Since TotalBloodTestTime is already required to be non-negative by its variable definition,
# no additional constraint is needed for TotalBloodTestTime >= 0.
# TotalBloodTestTime.addVar includes the non-negativity constraint implicitly by setting vtype=gp.GRB.CONTINUOUS.

# Constraint: The time spent on ear tests must be non-negative
model.addConstr(TotalEarTestTime >= 0, name="non_negative_ear_test_time")

# Add constraint for blood tests to ear tests ratio
model.addConstr(NumberBloodTests >= BloodEarRatio * NumberEarTests, name="blood_to_ear_test_ratio")

# Ensure at least the minimum number of ear tests are administered
model.addConstr(NumberEarTests >= MinEarTests, name="min_ear_tests")

# Add time constraint for tests
model.addConstr(TotalBloodTestTime + TotalEarTestTime <= TotalTime, "total_time_constraint")

# Constraint for Total Ear Test Time
model.addConstr(TotalEarTestTime == EarTestTime * NumberEarTests, name="Total_Ear_Test_Time")

# Constraint for total time spent on blood tests
model.addConstr(TotalBloodTestTime == NumberBloodTests * BloodTestTime, name="total_blood_test_time")

# Add constraint for total time spent on blood tests
model.addConstr(TotalBloodTestTime == NumberBloodTests * BloodTestTime, name="total_blood_test_time")

# Total time spent on ear tests is the number of ear tests times the time per test
TotalEarTestTime_const = model.addConstr(TotalEarTestTime == NumberEarTests * EarTestTime, name="TotalEarTestTime_constraint")

# Add constraint to equate time spent on blood tests to the time per blood test times the number of blood tests
model.addConstr(TotalBloodTestTime == BloodTestTime * NumberBloodTests, name="blood_test_time_constraint")

# Add ear testing time constraint
model.addConstr(TotalEarTestTime == EarTestTime * NumberEarTests, name="ear_test_time_constraint")

# Add constraint to ensure clinic does not operate beyond its total operational time available
model.addConstr(TotalBloodTestTime + TotalEarTestTime <= TotalTime, name="clinic_operational_time")

# Maintain the minimum ratio of blood tests to ear tests
model.addConstr(NumberBloodTests >= BloodEarRatio * NumberEarTests, name="min_blood_ear_ratio")

# Ensure the number of ear tests meets the minimum required
model.addConstr(NumberEarTests >= MinEarTests, name="min_ear_tests")

# Set objective
model.setObjective(NumberBloodTests + NumberEarTests, gp.GRB.MAXIMIZE)

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
