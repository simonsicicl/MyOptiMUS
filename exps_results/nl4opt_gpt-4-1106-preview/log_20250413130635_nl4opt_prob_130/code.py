import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_130/data.json", "r") as f:
    data = json.load(f)

LegMedicinePainKiller1 = data["LegMedicinePainKiller1"] # scalar parameter
BackMedicinePainKiller1 = data["BackMedicinePainKiller1"] # scalar parameter
LegMedicinePainKiller2 = data["LegMedicinePainKiller2"] # scalar parameter
BackMedicinePainKiller2 = data["BackMedicinePainKiller2"] # scalar parameter
SleepMedicinePainKiller1 = data["SleepMedicinePainKiller1"] # scalar parameter
SleepMedicinePainKiller2 = data["SleepMedicinePainKiller2"] # scalar parameter
MaxSleepMedicine = data["MaxSleepMedicine"] # scalar parameter
MinLegMedicine = data["MinLegMedicine"] # scalar parameter
DosesPainKiller1 = model.addVar(vtype=gp.GRB.INTEGER, name="DosesPainKiller1")
DosesPainKiller2 = model.addVar(vtype=gp.GRB.INTEGER, name="DosesPainKiller2")

# Add constraint to ensure non-negativity of the doses of pain killer 1
model.addConstr(DosesPainKiller1 >= 0, name="doses_painkiller1_nonnegativity")

# Since the variable DosesPainKiller2 is already defined as non-negative in its declaration, no additional code is needed for this constraint.

# Add constraint: Total amount of sleep medicine from both pain killers is at most MaxSleepMedicine units
model.addConstr(SleepMedicinePainKiller1 * DosesPainKiller1 + SleepMedicinePainKiller2 * DosesPainKiller2 <= MaxSleepMedicine, "Max_sleep_medicine")

# Add constraint: Total amount of leg medicine from both pain killers is at least MinLegMedicine units
model.addConstr(LegMedicinePainKiller1 * DosesPainKiller1 + LegMedicinePainKiller2 * DosesPainKiller2 >= MinLegMedicine, name="min_leg_medicine_requirement")

# Add constraint for the total sleep medicine from all pain killers not exceeding the maximum limit
model.addConstr(SleepMedicinePainKiller1 * DosesPainKiller1 + SleepMedicinePainKiller2 * DosesPainKiller2 <= MaxSleepMedicine, name="max_sleep_medicine")

# Add constraint for minimum requirement of total leg medicine from all pain killers
model.addConstr(LegMedicinePainKiller1 * DosesPainKiller1 + LegMedicinePainKiller2 * DosesPainKiller2 >= MinLegMedicine, name="min_leg_medicine_requirement")

# Objective function
model.setObjective(BackMedicinePainKiller1 * DosesPainKiller1 + BackMedicinePainKiller2 * DosesPainKiller2, gp.GRB.MAXIMIZE)

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
