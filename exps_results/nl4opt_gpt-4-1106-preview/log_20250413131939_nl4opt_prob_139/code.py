import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_139/data.json", "r") as f:
    data = json.load(f)

SpitTestTime = data["SpitTestTime"] # scalar parameter
SwabTestTime = data["SwabTestTime"] # scalar parameter
SpitSwabRatio = data["SpitSwabRatio"] # scalar parameter
MinSwabs = data["MinSwabs"] # scalar parameter
TotalTime = data["TotalTime"] # scalar parameter
NumberOfSpitTests = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfSpitTests")
NumberOfSwabs = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfSwabs")

# Add constraint for the total time spent on spit tests and swabs not exceeding total operation time
model.addConstr(SpitTestTime * NumberOfSpitTests + SwabTestTime * NumberOfSwabs <= TotalTime, name="total_test_time_constraint")

# Add constraint to ensure the number of spit tests is at least SpitSwabRatio times the number of swabs
model.addConstr(NumberOfSpitTests >= SpitSwabRatio * NumberOfSwabs, name="spit_to_swab_ratio")

# Add non-negativity constraint for the number of spit tests
model.addConstr(NumberOfSpitTests >= 0, name="nonnegativity_spit_tests")

# Since NumberOfSwabs is already defined as an integer variable, no additional constraint is needed
# to ensure non-negativity. Integer variables in Gurobi are non-negative by default.

# Add constraint for minimum number of swabs
model.addConstr(NumberOfSwabs >= MinSwabs, name="min_swabs")

# Ensure the minimum number of swabs is administered
model.addConstr(NumberOfSwabs >= MinSwabs, name="min_swabs_requirement")

# Constraint to maintain minimum ratio of spit tests to swabs
model.addConstr(NumberOfSpitTests >= SpitSwabRatio * NumberOfSwabs, name="SpitSwabRatioConstraint")

# Add constraint for the time to administer tests not exceeding clinic's total operation time
model.addConstr(SpitTestTime * NumberOfSpitTests + SwabTestTime * NumberOfSwabs <= TotalTime, "clinic_operation_time")

# Ensure the minimum number of swabs is respected
model.addConstr(NumberOfSwabs >= MinSwabs, name="min_swabs_constraint")

# Constraint: The number of spit tests must be at least twice the number of swabs
model.addConstr(NumberOfSpitTests >= SpitSwabRatio * NumberOfSwabs, "SpitTestSwabConstraint")

# Set objective
model.setObjective(NumberOfSpitTests + NumberOfSwabs, gp.GRB.MAXIMIZE)

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
