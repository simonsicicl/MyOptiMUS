import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_77/data.json", "r") as f:
    data = json.load(f)

DualCap = data["DualCap"] # scalar parameter
SingleCap = data["SingleCap"] # scalar parameter
DualGlue = data["DualGlue"] # scalar parameter
SingleGlue = data["SingleGlue"] # scalar parameter
MinLetters = data["MinLetters"] # scalar parameter
MaxGlue = data["MaxGlue"] # scalar parameter
DualModelMachines = model.addVar(vtype=gp.GRB.INTEGER, name="DualModelMachines")
SingleModelMachines = model.addVar(vtype=gp.GRB.INTEGER, name="SingleModelMachines")

# The variable DualModelMachines is already defined as an integer. No additional constraint is required.

# The variable SingleModelMachines is already defined as an integer. No additional constraint is required.

# Since DualModelMachines is already required to be integer, non-negativity is implicit
# Hence, no additional constraint needs to be added for this condition

# Since the variable SingleModelMachines is already guaranteed to be non-negative by its definition as an integer variable in Gurobi, no additional constraint is needed.
# However, if we want to explicitly add this redundant constraint, we could do the following.
model.addConstr(SingleModelMachines >= 0, name="non_negative_single_model_machines")

# Add constraint for total stamping capacity of all machines
model.addConstr(DualModelMachines * DualCap + SingleModelMachines * SingleCap >= MinLetters, name="stamping_capacity")

# Add constraint for maximum glue usage per minute
model.addConstr(DualGlue * DualModelMachines + SingleGlue * SingleModelMachines <= MaxGlue, name="max_glue_usage")

# Add capacity constraint for dual model machines
model.addConstr(DualModelMachines * DualCap >= MinLetters, name="dual_capacity_constraint")

# Since the constraint is an inequality and the related variable's integrality
# doesn't need to change, we can directly write the constraint.
model.addConstr(SingleModelMachines * SingleCap >= 0, name="total_capacity_constraint")

# Total glue consumption by dual model stamping machines should not exceed the maximum glue consumption
model.addConstr(DualModelMachines * DualGlue <= MaxGlue, "max_glue_consumption")

# Add maximum glue consumption constraint for single model stamping machines
model.addConstr(SingleModelMachines * SingleGlue <= MaxGlue, name="max_glue_consumption")

model.addConstr(SingleModelMachines - DualModelMachines >= 1, name='single_gt_dual_constraint')

# Ensure that the total stamping capacity per minute meets or exceeds the minimum requirement
model.addConstr(DualModelMachines * DualCap + SingleModelMachines * SingleCap >= MinLetters, name="stamping_capacity")

# Ensure glue consumption per minute does not exceed the maximum limit
model.addConstr(DualModelMachines * DualGlue + SingleModelMachines * SingleGlue <= MaxGlue, "glue_consumption_limit")

# Set objective
model.setObjective(DualModelMachines + SingleModelMachines, gp.GRB.MINIMIZE)

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
