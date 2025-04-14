import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_100/data.json", "r") as f:
    data = json.load(f)

PainPillOne = data["PainPillOne"] # scalar parameter
AnxietyPillOne = data["AnxietyPillOne"] # scalar parameter
DischargePillOne = data["DischargePillOne"] # scalar parameter
PainPillTwo = data["PainPillTwo"] # scalar parameter
AnxietyPillTwo = data["AnxietyPillTwo"] # scalar parameter
DischargePillTwo = data["DischargePillTwo"] # scalar parameter
MaxPainMedication = data["MaxPainMedication"] # scalar parameter
MinAnxietyMedication = data["MinAnxietyMedication"] # scalar parameter
x_1 = model.addVar(vtype=gp.GRB.CONTINUOUS, name="x_1")
x_2 = model.addVar(vtype=gp.GRB.CONTINUOUS, name="x_2")

# Add non-negativity constraint for Pill 1
model.addConstr(x_1 >= 0, name="non_negativity_pill_1")

# Ensure that the number of units of Pill 2 is non-negative
model.addConstr(x_2 >= 0, name="pill2_non_negative")

# Add constraint for maximum allowed pain medication
model.addConstr(PainPillOne * x_1 + PainPillTwo * x_2 <= MaxPainMedication, name="max_pain_medication")

# Add constraint for the minimum anxiety medication required
model.addConstr(AnxietyPillOne * x_1 + AnxietyPillTwo * x_2 >= MinAnxietyMedication, name="min_anxiety_med")

# Add constraint for the maximum allowed pain medication
model.addConstr(PainPillOne * x_1 + PainPillTwo * x_2 <= MaxPainMedication, name="max_pain_medication")

# Constraint: The total units of anxiety medication must meet or exceed the minimum required
model.addConstr(AnxietyPillOne * x_1 + AnxietyPillTwo * x_2 >= MinAnxietyMedication, name="min_anxiety_medication")

# Objective: Minimize the total discharge from the medication plan
model.setObjective(DischargePillOne * x_1 + DischargePillTwo * x_2, gp.GRB.MINIMIZE)

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
