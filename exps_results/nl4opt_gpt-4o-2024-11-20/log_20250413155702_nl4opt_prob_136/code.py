import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_136/data.json", "r") as f:
    data = json.load(f)

HeartLab1 = data["HeartLab1"] # scalar parameter
LungLab1 = data["LungLab1"] # scalar parameter
HeartLab2 = data["HeartLab2"] # scalar parameter
LungLab2 = data["LungLab2"] # scalar parameter
WorkerLab1 = data["WorkerLab1"] # scalar parameter
WorkerLab2 = data["WorkerLab2"] # scalar parameter
TotalWorkerHours = data["TotalWorkerHours"] # scalar parameter
MinHeartPills = data["MinHeartPills"] # scalar parameter
MinLungPills = data["MinLungPills"] # scalar parameter
HoursLab1 = model.addVar(vtype=gp.GRB.CONTINUOUS, name="HoursLab1")
HoursLab2 = model.addVar(vtype=gp.GRB.CONTINUOUS, name="HoursLab2")

# Ensure the number of hours allocated to Lab 1 is non-negative
model.addConstr(HoursLab1 >= 0, name="non_negative_hours_lab1")

# No additional code needed since the variable "HoursLab2" is already defined with non-negativity (vtype=gp.GRB.CONTINUOUS automatically enforces non-negativity).

# Add total worker hours constraint
model.addConstr(HoursLab1 + HoursLab2 <= TotalWorkerHours, name="total_worker_hours_constraint")

# Add constraint to ensure total heart medication production meets the minimum requirement
model.addConstr(
    HeartLab1 * HoursLab1 + HeartLab2 * HoursLab2 >= MinHeartPills,
    name="min_heart_pills_constraint"
)

# Add constraint to ensure total lung medication pills produced meets the minimum requirement
model.addConstr(LungLab1 * HoursLab1 + LungLab2 * HoursLab2 >= MinLungPills, name="min_lung_pills_requirement")

# Add constraint to ensure total heart medication pills meet the minimum requirement
model.addConstr(
    HoursLab1 * HeartLab1 + HoursLab2 * HeartLab2 >= MinHeartPills,
    name="min_heart_pills"
)

# Add constraint to ensure total lung medication pills meet the minimum requirement
model.addConstr(
    LungLab1 * HoursLab1 + LungLab2 * HoursLab2 >= MinLungPills,
    name="min_lung_pills"
)

# Add constraint to ensure total worker hours used across Labs 1 and 2 do not exceed available hours
model.addConstr(
    HoursLab1 * WorkerLab1 + HoursLab2 * WorkerLab2 <= TotalWorkerHours,
    name="total_worker_hours_limit"
)

# Set objective
model.setObjective(WorkerLab1 * HoursLab1 + WorkerLab2 * HoursLab2, gp.GRB.MINIMIZE)

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
