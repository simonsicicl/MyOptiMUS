import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_103/data.json", "r") as f:
    data = json.load(f)

TotalMedication = data["TotalMedication"] # scalar parameter
SmallMedication = data["SmallMedication"] # scalar parameter
SmallMeat = data["SmallMeat"] # scalar parameter
LargeMedication = data["LargeMedication"] # scalar parameter
LargeMeat = data["LargeMeat"] # scalar parameter
MinSmallBonePercentage = data["MinSmallBonePercentage"] # scalar parameter
MinLargeBones = data["MinLargeBones"] # scalar parameter
SmallBones = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SmallBones")
LargeBones = model.addVar(vtype=gp.GRB.CONTINUOUS, name="LargeBones")

# Add constraint to limit total tooth medication usage
model.addConstr(SmallBones * SmallMedication + LargeBones * LargeMedication <= TotalMedication, name="medication_limit")

# Add constraint to ensure at least MinSmallBonePercentage of all bones produced are small
model.addConstr((1 - MinSmallBonePercentage) * SmallBones >= MinSmallBonePercentage * LargeBones, name="min_small_bone_percentage")

# Add constraint to ensure at least MinLargeBones large bones are produced
model.addConstr(LargeBones >= MinLargeBones, name="min_large_bones")

# No code is needed: Gurobi variables by default have non-negativity constraints unless otherwise specified (e.g., if set to unrestricted or negative bounds).

# The variable LargeBones is already coded as a continuous variable. No additional code is needed for non-negativity since Gurobi variables are non-negative by default unless specified otherwise.

# Add constraint for total tooth medication usage
model.addConstr(SmallMedication * SmallBones + LargeMedication * LargeBones <= TotalMedication, name="medication_usage")

# Add constraint to ensure a minimum fraction of total bones produced are small bones
model.addConstr((1 - MinSmallBonePercentage) * SmallBones >= MinSmallBonePercentage * LargeBones, name="min_small_bones_percentage")

# Add constraint to ensure at least the minimum number of large bones are produced
model.addConstr(LargeBones >= MinLargeBones, name="min_large_bones")

# Set objective
model.setObjective(SmallMeat * SmallBones + LargeMeat * LargeBones, gp.GRB.MINIMIZE)

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
