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
NumberOfVitaminShotBatches = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfVitaminShotBatches")
NumberOfVitaminPillBatches = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfVitaminPillBatches")

# Since the variable NumberOfVitaminShotBatches is already ensured to be an integer,
# the only constraint needed is that it must be non-negative which is handled by the variable type,
# hence no additional code is needed for this constraint.

# Since the variable is already defined as an integer, we just need to add the non-negative constraint
model.addConstr(NumberOfVitaminPillBatches >= 0, name="nonnegativity_vitamin_pill_batches")

# Add constraint ensuring number of vitamin pill batches is larger than the number of vitamin shot batches
model.addConstr(NumberOfVitaminPillBatches >= NumberOfVitaminShotBatches + 1, "NumberOfVitaminPillBatches_geq_NumberOfVitaminShotBatches")

# Add constraint for maximum number of vitamin shot batches the clinic can produce
model.addConstr(NumberOfVitaminShotBatches <= MaxShotBatches, "max_shot_batch_constraint")

# Add constraint to ensure the clinic's production does not exceed available units of vitamin C
model.addConstr(NumberOfVitaminShotBatches * VitaminCShot + NumberOfVitaminPillBatches * VitaminCPill <= TotalVitaminC, "Vitamin_C_Constraint")

# Add constraint to ensure the clinic's production does not exceed available units of vitamin D
model.addConstr(NumberOfVitaminShotBatches * VitaminDShot + NumberOfVitaminPillBatches * VitaminDPill <= TotalVitaminD, "VitaminD_Capacity")

# Add constraint for the maximum number of vitamin shot batches the clinic can produce
model.addConstr(NumberOfVitaminShotBatches <= MaxShotBatches, name="max_vitamin_shot_batches")

# Define the objective function
model.setObjective(NumberOfVitaminShotBatches * PeoplePerShot + NumberOfVitaminPillBatches * PeoplePerPill, gp.GRB.MAXIMIZE)

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
