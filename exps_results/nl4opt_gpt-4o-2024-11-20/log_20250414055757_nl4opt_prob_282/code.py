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
PHTests = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PHTests")
SalinityTests = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SalinityTests")

# Add constraint to ensure at least MinPHTests pH tests are performed
model.addConstr(PHTests >= MinPHTests, name="min_pH_tests")

# Add constraint to ensure total tests (pH and salinity) meet or exceed the minimum required
model.addConstr(PHTests + SalinityTests >= MinTotalTests, name="min_total_tests")

# Add constraint to ensure the number of pH tests does not exceed MaxPHSalinityRatio times the number of salinity tests
model.addConstr(PHTests <= MaxPHSalinityRatio * SalinityTests, name="PHTests_max_ratio_salinity")

# Non-negativity constraint for SalinityTests
model.addConstr(SalinityTests >= 0, name="non_negative_salinity_tests")

# The non-negativity constraint for PHTests is implicitly satisfied by its continuous type which is non-negative by default in Gurobi. Hence, no additional code is required.

# Add constraint to ensure the number of pH tests is at least the minimum required
model.addConstr(PHTests >= MinPHTests, name="min_ph_tests")

# Add constraint to ensure the total number of tests meets the minimum requirement
model.addConstr(PHTests + SalinityTests >= MinTotalTests, name="min_total_tests_constraint")

# Add constraint to restrict the ratio of pH tests to salinity tests
model.addConstr(PHTests <= MaxPHSalinityRatio * SalinityTests, name="MaxPHSalinityRatio_Constraint")

# Set objective
model.setObjective(ProbesSalinity * SalinityTests + ProbesPH * PHTests, gp.GRB.MINIMIZE)

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
