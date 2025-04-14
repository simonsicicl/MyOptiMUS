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
NumPainkillerPills = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumPainkillerPills")
NumSleepingPills = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumSleepingPills")
TotalPills = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalPills")

# Add total morphine usage constraint
model.addConstr(
    MorphinePainkiller * NumPainkillerPills + MorphineSleepingPill * NumSleepingPills <= TotalMorphine,
    name="total_morphine_constraint"
)

# Add constraint to ensure at least the minimum number of painkiller pills are produced
model.addConstr(NumPainkillerPills >= MinPainkillers, name="min_painkiller_constraint")

# Add constraint to ensure at least MinProportionSleepingPills of TotalPills are sleeping pills
model.addConstr(NumSleepingPills >= MinProportionSleepingPills * TotalPills, 
                name="min_proportion_sleeping_pills")

# Add non-negativity constraint for the total number of painkiller pills
model.addConstr(NumPainkillerPills >= 0, name="non_negative_painkiller_pills")

# The variable "NumSleepingPills" is already non-negative due to its default lower bound (0) in Gurobi.

# Add constraint: TotalPills equals the sum of NumSleepingPills and NumPainkillerPills
model.addConstr(TotalPills == NumSleepingPills + NumPainkillerPills, name="TotalPills_constraint")

# Add total morphine usage constraint
model.addConstr(
    MorphinePainkiller * NumPainkillerPills + MorphineSleepingPill * NumSleepingPills <= TotalMorphine,
    name="total_morphine_usage"
)

# Add constraint for minimum production of painkiller pills
model.addConstr(NumPainkillerPills >= MinPainkillers, name="min_painkiller_production")

# Add constraint to ensure a minimum proportion of sleeping pills is maintained
model.addConstr(NumSleepingPills >= MinProportionSleepingPills * (NumPainkillerPills + NumSleepingPills), name="min_proportion_sleeping_pills")

# Add total pills production constraint
model.addConstr(TotalPills == NumPainkillerPills + NumSleepingPills, name="total_pills_production")

# Set objective
model.setObjective(DigestiveMedicinePainkiller * NumPainkillerPills + DigestiveMedicineSleepingPill * NumSleepingPills, gp.GRB.MINIMIZE)

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
