import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_282/data.json", "r") as f:
    data = json.load(f)

ProbesSalinity = data["ProbesSalinity"] # scalar parameter
ProbesPH = data["ProbesPH"] # scalar parameter
MinPHTests = data["MinPHTests"] # scalar parameter
MinTotalTests = data["MinTotalTests"] # scalar parameter
MaxPHSalinityRatio = data["MaxPHSalinityRatio"] # scalar parameter
NumberOfPHTests = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfPHTests")
NumberOfSalinityTests = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfSalinityTests")

# Ensure that the number of pH tests performed is at least the minimum required
model.addConstr(NumberOfPHTests >= MinPHTests, name="min_pH_tests")

# Add constraint to ensure the total number of tests meets the minimum required tests
model.addConstr(NumberOfPHTests + NumberOfSalinityTests >= MinTotalTests, name="min_total_tests")

# Add constraint for the maximum number of pH tests in relation to salinity tests
model.addConstr(NumberOfPHTests <= MaxPHSalinityRatio * NumberOfSalinityTests, name="PH_to_Salinity_Ratio")

model.addConstr(NumberOfSalinityTests >= 0, name="non_negative_salinity_tests")

# The number of pH tests is non-negative
model.addConstr(NumberOfPHTests >= 0, name="non_negative_pH_tests")

# Minimum number of pH tests performed constraint
model.addConstr(NumberOfPHTests >= MinPHTests, name="min_pH_tests")

# Add the constraint for the total minimum number of tests
model.addConstr(NumberOfPHTests + NumberOfSalinityTests >= MinTotalTests, name="min_total_tests_constraint")

# Maximum ratio of pH tests to salinity tests constraint
model.addConstr(NumberOfPHTests <= MaxPHSalinityRatio * NumberOfSalinityTests, "Max_PH_Salinity_Ratio_Constraint")

# Set objective function
model.setObjective(NumberOfPHTests * ProbesPH + NumberOfSalinityTests * ProbesSalinity, gp.GRB.MINIMIZE)

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
