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
PillOneUnits = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PillOneUnits")
PillTwoUnits = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PillTwoUnits")

# Since the variable PillOneUnits is already defined with non-negativity (vtype=gp.GRB.CONTINUOUS), no additional constraint is required.

# No additional code is needed since the variable 'PillTwoUnits' is already defined as non-negative,
# which is the default for continuous variables in Gurobi.

# Add constraint: total pain medication provided by Pill 1 and Pill 2 must not exceed MaxPainMedication
model.addConstr((PainPillOne * PillOneUnits) + (PainPillTwo * PillTwoUnits) <= MaxPainMedication, name="pain_medication_limit")

# Add constraint to ensure combined anxiety medication is at least the minimum required 
model.addConstr(PillOneUnits * AnxietyPillOne + PillTwoUnits * AnxietyPillTwo >= MinAnxietyMedication, name="min_anxiety_medication")

# Add constraint to limit total pain medication provided by both pills
model.addConstr(
    PillOneUnits * PainPillOne + PillTwoUnits * PainPillTwo <= MaxPainMedication,
    name="pain_medication_limit"
)

# Add constraint to ensure the total amount of anxiety medication meets the minimum required
model.addConstr(
    AnxietyPillOne * PillOneUnits + AnxietyPillTwo * PillTwoUnits >= MinAnxietyMedication, 
    name="minimum_anxiety_medication"
)

# Set objective
model.setObjective(DischargePillOne * PillOneUnits + DischargePillTwo * PillTwoUnits, gp.GRB.MINIMIZE)

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
