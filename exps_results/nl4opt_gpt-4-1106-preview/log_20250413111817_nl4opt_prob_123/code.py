import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_123/data.json", "r") as f:
    data = json.load(f)

TotalMorphine = data["TotalMorphine"] # scalar parameter
MorphinePainkiller = data["MorphinePainkiller"] # scalar parameter
MorphineSleepingPill = data["MorphineSleepingPill"] # scalar parameter
DigestiveMedicinePainkiller = data["DigestiveMedicinePainkiller"] # scalar parameter
DigestiveMedicineSleepingPill = data["DigestiveMedicineSleepingPill"] # scalar parameter
MinPainkillers = data["MinPainkillers"] # scalar parameter
MinProportionSleepingPills = data["MinProportionSleepingPills"] # scalar parameter
PainkillerPillsProduced = model.addVar(vtype=gp.GRB.INTEGER, name="PainkillerPillsProduced")
SleepingPillsProduced = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SleepingPillsProduced")

# Total morphine used constraint
model.addConstr(MorphinePainkiller * PainkillerPillsProduced + MorphineSleepingPill * SleepingPillsProduced <= TotalMorphine, name="total_morphine_used")

# Add constraint to ensure the minimum production of painkiller pills
model.addConstr(PainkillerPillsProduced >= MinPainkillers, name="min_painkillers_produced")

# Constraint: At least a minimum proportion of the total pills produced should be sleeping pills
model.addConstr(SleepingPillsProduced >= MinProportionSleepingPills * (SleepingPillsProduced + PainkillerPillsProduced), 
                name="min_proportion_sleeping_pills")

# Since PainkillerPillsProduced is already a non-negative integer variable, no constraint is needed to enforce this.
# Gurobi variables are non-negative by default unless specified.

# Add constraint for non-negativity of the number of sleeping pills produced
model.addConstr(SleepingPillsProduced >= 0, name="non_negative_sleeping_pills_produced")

# Total amount of morphine used cannot exceed the total amount available constraint
model.addConstr(MorphinePainkiller * PainkillerPillsProduced + MorphineSleepingPill * SleepingPillsProduced <= TotalMorphine, "TotalMorphineConstraint")

# Add constraint to ensure the minimum number of painkiller pills is produced
model.addConstr(PainkillerPillsProduced >= MinPainkillers, name="min_painkiller_production")

# Add constraint to ensure that at least a certain proportion of the total pills must be sleeping pills
model.addConstr(SleepingPillsProduced >= MinProportionSleepingPills * (PainkillerPillsProduced + SleepingPillsProduced), "min_sleeping_pills_proportion")

# Set objective
model.setObjective(DigestiveMedicinePainkiller * PainkillerPillsProduced + DigestiveMedicineSleepingPill * SleepingPillsProduced, gp.GRB.MINIMIZE)

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
