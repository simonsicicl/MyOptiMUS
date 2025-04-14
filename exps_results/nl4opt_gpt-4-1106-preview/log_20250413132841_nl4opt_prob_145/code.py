import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_145/data.json", "r") as f:
    data = json.load(f)

PainKillersProcess1 = data["PainKillersProcess1"] # scalar parameter
SleepingPillsProcess1 = data["SleepingPillsProcess1"] # scalar parameter
PainKillersProcess2 = data["PainKillersProcess2"] # scalar parameter
SleepingPillsProcess2 = data["SleepingPillsProcess2"] # scalar parameter
MaterialProcess1 = data["MaterialProcess1"] # scalar parameter
MaterialProcess2 = data["MaterialProcess2"] # scalar parameter
TotalMaterial = data["TotalMaterial"] # scalar parameter
MinPainKillers = data["MinPainKillers"] # scalar parameter
MinSleepingPills = data["MinSleepingPills"] # scalar parameter
HoursProcess1 = model.addVar(vtype=gp.GRB.CONTINUOUS, name="HoursProcess1")
HoursProcess2 = model.addVar(vtype=gp.GRB.CONTINUOUS, name="HoursProcess2")

# Add non-negativity constraint for HoursProcess1
model.addConstr(HoursProcess1 >= 0, name="non_negativity_HoursProcess1")

model.addConstr(HoursProcess2 >= 0, name="constraint_non_negative_hours_process2")

# Add constraint to ensure total material used by both processes does not exceed total available material units
model.addConstr(MaterialProcess1 * HoursProcess1 + MaterialProcess2 * HoursProcess2 <= TotalMaterial, name="material_usage")

# At least MinPainKillers units of pain killers must be produced
model.addConstr(PainKillersProcess1 * HoursProcess1 + PainKillersProcess2 * HoursProcess2 >= MinPainKillers, name="min_painkillers")

# Add constraint for minimum production of sleeping pills
model.addConstr(SleepingPillsProcess1 * HoursProcess1 + SleepingPillsProcess2 * HoursProcess2 >= MinSleepingPills, name="MinSleepingPillsProduction")

# Ensure the total production of pain killers meets or exceeds the minimum required
model.addConstr(PainKillersProcess1 * HoursProcess1 + PainKillersProcess2 * HoursProcess2 >= MinPainKillers, name="min_production")

# Ensure the total production of sleeping pills meets or exceeds the minimum required
model.addConstr(SleepingPillsProcess1 * HoursProcess1 + SleepingPillsProcess2 * HoursProcess2 >= MinSleepingPills, name="min_sleeping_pills_production")

# Constraint for the total use of preliminary material not exceeding the total amount available
model.addConstr(MaterialProcess1 * HoursProcess1 + MaterialProcess2 * HoursProcess2 <= TotalMaterial, "total_material_use")

# Set objective
model.setObjective(HoursProcess1 + HoursProcess2, gp.GRB.MINIMIZE)

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
