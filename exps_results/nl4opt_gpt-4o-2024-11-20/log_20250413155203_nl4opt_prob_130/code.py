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
DosesPainKiller1 = model.addVar(vtype=gp.GRB.CONTINUOUS, name="DosesPainKiller1")
DosesPainKiller2 = model.addVar(vtype=gp.GRB.CONTINUOUS, name="DosesPainKiller2")

# Add non-negativity constraint for DosesPainKiller1
model.addConstr(DosesPainKiller1 >= 0, name="non_negativity_DosesPainKiller1")

# No additional code needed as the non-negativity constraint is implicitly enforced by the variable type (vtype=gp.GRB.CONTINUOUS).

# Add constraint to limit total sleep medicine from doses of pain killer 1 and 2
model.addConstr(
    SleepMedicinePainKiller1 * DosesPainKiller1 + SleepMedicinePainKiller2 * DosesPainKiller2 <= MaxSleepMedicine,
    name="total_sleep_medicine_constraint"
)

# Add constraint for the minimum total units of leg medicine
model.addConstr(LegMedicinePainKiller1 * DosesPainKiller1 + LegMedicinePainKiller2 * DosesPainKiller2 >= MinLegMedicine, name="min_leg_medicine")

# Add constraint: Total sleep medicine must not exceed the maximum allowed  
model.addConstr(  
    SleepMedicinePainKiller1 * DosesPainKiller1 + SleepMedicinePainKiller2 * DosesPainKiller2 <= MaxSleepMedicine,  
    name="TotalSleepMedicineConstraint"  
)

# Add constraint to ensure total leg medicine meets the minimum requirement  
model.addConstr(  
    DosesPainKiller1 * LegMedicinePainKiller1 + DosesPainKiller2 * LegMedicinePainKiller2 >= MinLegMedicine,  
    name="min_leg_medicine"  
)

# Set objective
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
