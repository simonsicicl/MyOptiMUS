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
SmallBoneMedicationUnits = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SmallBoneMedicationUnits")
LargeBoneMedicationUnits = model.addVar(vtype=gp.GRB.CONTINUOUS, name="LargeBoneMedicationUnits")

# Constraint for the maximum units of tooth medication used for small and large bones
model.addConstr(SmallBoneMedicationUnits * SmallMedication + LargeBoneMedicationUnits * LargeMedication <= TotalMedication, name="total_medication_limit")

# Add constraint to ensure at least MinSmallBonePercentage of all bones made are small
model.addConstr(SmallBoneMedicationUnits >= MinSmallBonePercentage * (SmallBoneMedicationUnits + LargeBoneMedicationUnits), name="MinSmallBonePercentageConstraint")

# Add constraint to ensure at least MinLargeBones large bones must be made
model.addConstr(LargeBoneMedicationUnits >= MinLargeBones * LargeMedication, name="min_large_bones")

# The SmallBoneMedicationUnits variable is already defined as continuous which means it can take on non-negative values by default.
# Therefore, no further constraint is needed to ensure non-negativity.

# The number of large bones produced must be non-negative
model.addConstr(LargeBoneMedicationUnits >= 0, name="non_negative_large_bone")

# Ensure the total medication used for small and large bones does not exceed the total medication available
model.addConstr(SmallBoneMedicationUnits * SmallMedication + LargeBoneMedicationUnits * LargeMedication <= TotalMedication, "medication_limit")

# Ensure that at least the minimum number of large bones are made
model.addConstr(LargeBoneMedicationUnits * LargeMedication >= MinLargeBones * LargeMedication, name="min_large_bones")

# Ensure that the number of small bones is at least half the total number of bones produced
model.addConstr(SmallBoneMedicationUnits >= MinSmallBonePercentage * (SmallBoneMedicationUnits + LargeBoneMedicationUnits),
                name="min_small_bone_percentage")

# Define the objective function
model.setObjective(SmallBoneMedicationUnits * SmallMeat + LargeBoneMedicationUnits * LargeMeat, gp.GRB.MINIMIZE)

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
