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
NumberOfBloodTests = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfBloodTests")
NumberOfEarTests = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfEarTests")

# The variable "NumberOfBloodTests" is already defined as non-negative (CONTINUOUS type by default).

# Add non-negativity constraint for the number of ear tests
model.addConstr(NumberOfEarTests >= 0, name="non_negative_ear_tests")

# Add constraint to ensure NumberOfBloodTests is at least BloodEarRatio times NumberOfEarTests
model.addConstr(NumberOfBloodTests >= BloodEarRatio * NumberOfEarTests, name="blood_ear_ratio_constraint")

# Add minimum ear tests constraint
model.addConstr(NumberOfEarTests >= MinEarTests, name="min_ear_tests")

# Add time usage constraint
model.addConstr(NumberOfBloodTests * BloodTestTime + NumberOfEarTests * EarTestTime <= TotalTime, 
                name="time_usage_constraint")

# Add constraint to ensure the ratio of blood tests to ear tests is at least BloodEarRatio
model.addConstr(NumberOfBloodTests >= NumberOfEarTests * BloodEarRatio, name="blood_ear_ratio_constraint")

# Add minimum ear test constraint
model.addConstr(NumberOfEarTests >= MinEarTests, name="min_ear_tests")

# Add total time constraint ensuring tests do not exceed available operational time
model.addConstr(
    NumberOfBloodTests * BloodTestTime + NumberOfEarTests * EarTestTime <= TotalTime, 
    name="total_time_constraint"
)

# Add ratio constraint between blood tests and ear tests
model.addConstr(NumberOfBloodTests >= BloodEarRatio * NumberOfEarTests, name="blood_to_ear_ratio")

# Add constraint to ensure the number of ear tests is at least the specified minimum
model.addConstr(NumberOfEarTests >= MinEarTests, name="min_ear_tests_constraint")

# Set objective
model.setObjective(NumberOfBloodTests + NumberOfEarTests, gp.GRB.MAXIMIZE)

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
