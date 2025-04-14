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

# Ensure the number of hours process 1 is run is non-negative
model.addConstr(HoursProcess1 >= 0, name="non_negative_hours_process1")

# Add constraint for non-negativity of HoursProcess2
model.addConstr(HoursProcess2 >= 0, name="non_negativity_hours_process2")

# Add total material usage constraint
model.addConstr(
    HoursProcess1 * MaterialProcess1 + HoursProcess2 * MaterialProcess2 <= TotalMaterial,
    name="total_material_usage"
)

# Add constraint to ensure at least MinPainKillers units of pain killers are produced
model.addConstr(
    PainKillersProcess1 * HoursProcess1 + PainKillersProcess2 * HoursProcess2 >= MinPainKillers,
    name="MinPainKillersConstraint"
)

# Add constraint to ensure at least MinSleepingPills units of sleeping pills are produced
model.addConstr(
    SleepingPillsProcess1 * HoursProcess1 + SleepingPillsProcess2 * HoursProcess2 >= MinSleepingPills,
    name="min_sleeping_pills"
)

# Add total material usage constraint
model.addConstr(
    MaterialProcess1 * HoursProcess1 + MaterialProcess2 * HoursProcess2 <= TotalMaterial,
    name="total_material_usage"
)

# Add constraint to ensure the total amount of pain killers produced meets or exceeds the minimum required quantity
model.addConstr(HoursProcess1 * PainKillersProcess1 + HoursProcess2 * PainKillersProcess2 >= MinPainKillers, name="min_painkillers_constraint")

# Add constraint to ensure the total amount of sleeping pills produced meets or exceeds the minimum required
model.addConstr(SleepingPillsProcess1 * HoursProcess1 + SleepingPillsProcess2 * HoursProcess2 >= MinSleepingPills, name="min_sleeping_pills")

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
