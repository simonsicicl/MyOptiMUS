import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_118/data.json", "r") as f:
    data = json.load(f)

VitaminCShot = data["VitaminCShot"] # scalar parameter
VitaminDShot = data["VitaminDShot"] # scalar parameter
VitaminCPill = data["VitaminCPill"] # scalar parameter
VitaminDPill = data["VitaminDPill"] # scalar parameter
MaxShotBatches = data["MaxShotBatches"] # scalar parameter
TotalVitaminC = data["TotalVitaminC"] # scalar parameter
TotalVitaminD = data["TotalVitaminD"] # scalar parameter
PeoplePerShot = data["PeoplePerShot"] # scalar parameter
PeoplePerPill = data["PeoplePerPill"] # scalar parameter
NumShotBatches = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumShotBatches")
NumPillBatches = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumPillBatches")

# No additional code needed since the variable "NumShotBatches" is defined with non-negativity by default in Gurobi (continuous variables have a lower bound of 0 unless specified otherwise).

# Since NumPillBatches is already defined with non-negativity (vtype=gp.GRB.CONTINUOUS), no additional constraint is required.

# Add constraint: Number of vitamin pill batches must be at least 1 more than the number of vitamin shot batches
model.addConstr(NumPillBatches >= NumShotBatches + 1, name="pill_vs_shot_batches")

# Add constraint to ensure the number of vitamin shot batches produced does not exceed the maximum allowed  
model.addConstr(NumShotBatches <= MaxShotBatches, name="max_vitamin_batches_constraint")

# Add constraint: Vitamin C usage cannot exceed the total available units of vitamin C
model.addConstr(
    NumShotBatches * VitaminCShot + NumPillBatches * VitaminCPill <= TotalVitaminC,
    name="VitaminC_Usage_Constraint"
)

# Add constraint: Vitamin D usage cannot exceed the total available units of vitamin D
model.addConstr(
    VitaminDShot * NumShotBatches + VitaminDPill * NumPillBatches <= TotalVitaminD,
    name="VitaminD_usage_limit"
)

# Add constraint to ensure the number of vitamin shot batches does not exceed the maximum production limit
model.addConstr(NumShotBatches <= MaxShotBatches, name="vitamin_shot_batch_limit")

# No additional code is needed as the non-negativity constraint is automatically enforced by defining the decision variables as continuous (gp.GRB.CONTINUOUS) in Gurobi.

# Set objective
model.setObjective(PeoplePerShot * NumShotBatches + PeoplePerPill * NumPillBatches, gp.GRB.MAXIMIZE)

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
