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
HeartPillsProduced = model.addVar(vtype=gp.GRB.INTEGER, name="HeartPillsProduced")
LungPillsProduced = model.addVar(vtype=gp.GRB.INTEGER, name="LungPillsProduced")

model.addConstr(HoursLab1 >= 0, name="non_negativity_Lab1")

model.addConstr(HoursLab2 >= 0, name="min_hours_at_lab_2")

# Add constraint for total worker hours for both labs to be at most TotalWorkerHours
model.addConstr(HoursLab1 + HoursLab2 <= TotalWorkerHours, name="total_worker_hours")

# Add constraint for total production of heart medication pills to meet or exceed minimum required amount
model.addConstr(HeartLab1 * HoursLab1 + HeartLab2 * HoursLab2 >= MinHeartPills, name="min_heart_pills_req")

# Add constraint for minimum production of lung medication pills
model.addConstr(LungLab1 * HoursLab1 + LungLab2 * HoursLab2 >= MinLungPills, name="min_lung_pills_production")

# Ensure Lab 1 and Lab 2 produce at least the minimum required number of heart medication pills
model.addConstr(HeartLab1 * HoursLab1 + HeartLab2 * HoursLab2 >= MinHeartPills, name="min_heart_pills_requirement")

# Add constraint for minimum production of lung medication pills from Lab 1 and Lab 2
model.addConstr(LungLab1 * HoursLab1 + LungLab2 * HoursLab2 >= MinLungPills, name="min_lung_pills_production")

# Set objective
model.setObjective(HoursLab1 + HoursLab2, gp.GRB.MINIMIZE)

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
