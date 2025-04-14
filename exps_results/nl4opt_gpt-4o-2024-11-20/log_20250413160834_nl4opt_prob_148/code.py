import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_148/data.json", "r") as f:
    data = json.load(f)

PillTime = data["PillTime"] # scalar parameter
ShotTime = data["ShotTime"] # scalar parameter
RatioShotsToPills = data["RatioShotsToPills"] # scalar parameter
MinPills = data["MinPills"] # scalar parameter
TotalTime = data["TotalTime"] # scalar parameter
PillsAdministered = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PillsAdministered")
ShotsAdministered = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ShotsAdministered")

# Add constraint to ensure the clinic administers at least RatioShotsToPills times as many shots as pills
model.addConstr(ShotsAdministered >= RatioShotsToPills * PillsAdministered, name="ratio_shots_to_pills")

# Add constraint for minimum number of pill vaccines to be administered
model.addConstr(PillsAdministered >= MinPills, name="min_pills_constraint")

# Add total time constraint
model.addConstr(
    PillsAdministered * PillTime + ShotsAdministered * ShotTime <= TotalTime,
    name="total_time_constraint"
)

# The variable "PillsAdministered" is already defined as non-negative (continuous type). No additional constraints are needed.

# Non-negativity constraint for the number of shots administered
model.addConstr(ShotsAdministered >= 0, name="non_negativity_shots")

# Non-negativity constraint for the number of pill vaccines administered
model.addConstr(PillsAdministered >= 0, name="non_negativity_pills_administered")

# Add operational time constraint
model.addConstr(
    PillsAdministered * PillTime + ShotsAdministered * ShotTime <= TotalTime,
    name="operational_time_capacity"
)

# Add constraint for the ratio of shots to pills administered
model.addConstr(ShotsAdministered >= RatioShotsToPills * PillsAdministered, name="ratio_shots_to_pills")

# Add constraint to ensure at least the minimum number of pills are administered
model.addConstr(PillsAdministered >= MinPills, name="min_pills_constraint")

# Add constraint to ensure total vaccine administration time does not exceed clinic time
model.addConstr(
    PillsAdministered * PillTime + ShotsAdministered * ShotTime <= TotalTime,
    name="clinic_time_constraint"
)

# Add constraint to ensure the number of shots adminstered satisfies the minimum ratio
model.addConstr(ShotsAdministered >= RatioShotsToPills * PillsAdministered, name="min_ratio_shots_to_pills")

# Add constraint to ensure the minimum number of pills administered is met
model.addConstr(PillsAdministered >= MinPills, name="min_pills_constraint")

# Set objective
model.setObjective(PillsAdministered + ShotsAdministered, gp.GRB.MAXIMIZE)

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
