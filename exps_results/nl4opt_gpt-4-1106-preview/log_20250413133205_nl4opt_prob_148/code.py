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
ShotsAdministered = model.addVar(vtype=gp.GRB.INTEGER, name="ShotsAdministered")
PillsAdministered = model.addVar(vtype=gp.GRB.INTEGER, name="PillsAdministered")

# Administer at least RatioShotsToPills times as many shots as pills
model.addConstr(ShotsAdministered >= RatioShotsToPills * PillsAdministered, name="Shots_to_Pills_Ratio")

# Add minimum pill vaccine administration constraint
model.addConstr(PillsAdministered >= MinPills, name="min_pill_vaccines")

# Add constraint for the total time taken by all vaccines administrations
model.addConstr(PillsAdministered * PillTime + ShotsAdministered * ShotTime <= TotalTime, name="vaccine_administration_time")

# Add constraint to ensure the number of pill vaccines administered is non-negative
model.addConstr(PillsAdministered >= 0, name="PillsAdministered_non_negative")

# Add constraint to ensure the number of shot vaccines administered is non-negative
model.addConstr(ShotsAdministered >= 0, name="non_negative_shots")

# Constraint: Time used for administering vaccines must not exceed the clinic's total operating time
model.addConstr(PillsAdministered * PillTime + ShotsAdministered * ShotTime <= TotalTime, name="vaccine_administration_time")

# Ensure the minimum number of pill vaccines administered is satisfied
model.addConstr(PillsAdministered >= MinPills, "min_pills_administered")

# Administered shots must be at least a certain ratio times higher than the pill vaccines
model.addConstr(ShotsAdministered >= RatioShotsToPills * PillsAdministered, "min_ratio_shots_to_pills")

# Constraint: The total time for administering vaccines cannot exceed the total operating time of the clinic
ShotTime = data["ShotTime"] # scalar parameter
PillTime = data["PillTime"] # scalar parameter
TotalTime = data["TotalTime"] # scalar parameter

model.addConstr(ShotTime * ShotsAdministered + PillTime * PillsAdministered <= TotalTime, "clinic_time_limit")

# Administered shots must be at least the minimum ratio times the pills administered
model.addConstr(ShotsAdministered >= RatioShotsToPills * PillsAdministered, "min_shots_to_pills")

# Ensure the number of pills administered meets the minimum requirement
model.addConstr(PillsAdministered >= MinPills, "min_pills_requirement")

# Set objective
model.setObjective(ShotsAdministered + PillsAdministered, gp.GRB.MAXIMIZE)

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
