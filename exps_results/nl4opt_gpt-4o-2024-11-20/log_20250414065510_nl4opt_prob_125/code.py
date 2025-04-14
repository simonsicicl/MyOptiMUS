import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_125/data.json", "r") as f:
    data = json.load(f)

TAnxiety = data["TAnxiety"] # scalar parameter
TAntiDepressant = data["TAntiDepressant"] # scalar parameter
MinUnits = data["MinUnits"] # scalar parameter
MinAnxiety = data["MinAnxiety"] # scalar parameter
MaxAnxietyAntiDepressantRatio = data["MaxAnxietyAntiDepressantRatio"] # scalar parameter
AnxietyMedication = model.addVar(vtype=gp.GRB.CONTINUOUS, name="AnxietyMedication")
AntiDepressantMedication = model.addVar(vtype=gp.GRB.CONTINUOUS, name="AntiDepressantMedication")
WeightedTime = model.addVar(vtype=gp.GRB.CONTINUOUS, name="WeightedTime")

# Add constraint for the minimum total units of medication
model.addConstr(AnxietyMedication + AntiDepressantMedication >= MinUnits, name="min_total_medication")

# Add constraint to ensure AnxietyMedication is at least MinAnxiety
model.addConstr(AnxietyMedication >= MinAnxiety, name="min_anxiety_medication")

# Add constraint linking AnxietyMedication and AntiDepressantMedication with the maximum ratio
model.addConstr(AnxietyMedication <= MaxAnxietyAntiDepressantRatio * AntiDepressantMedication, name="max_anxiety_to_antidepressant_ratio")

# No code needed, as non-negativity is inherent to the variable type (CONTINUOUS in gurobipy)

# The non-negativity constraint is inherently satisfied as the variable AntiDepressantMedication is defined as continuous (non-negative by default)

# Add constraint for WeightedTime as a weighted average
model.addConstr(
    WeightedTime * (AnxietyMedication + AntiDepressantMedication) ==
    AnxietyMedication * TAnxiety + AntiDepressantMedication * TAntiDepressant,
    name="WeightedTime_calculation"
)

# Add constraint to ensure the total number of medication units prescribed meets the minimum requirement
model.addConstr(AnxietyMedication + AntiDepressantMedication >= MinUnits, name="medication_min_requirement")

# Add constraint to ensure minimum number of anxiety medication units are prescribed
model.addConstr(AnxietyMedication >= MinAnxiety, name="min_anxiety_med_constraint")

# Add constraint to ensure ratio of anxiety medication units to anti-depressant medication units does not exceed the maximum allowed limit
model.addConstr(AnxietyMedication <= MaxAnxietyAntiDepressantRatio * AntiDepressantMedication, name="anxiety_to_antidepressant_ratio")

# Set objective
model.setObjective(WeightedTime, gp.GRB.MINIMIZE)

# Add WeightedTime expression
model.addConstr(WeightedTime == TAnxiety * AnxietyMedication + TAntiDepressant * AntiDepressantMedication, "WeightedTimeConstraint")

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
