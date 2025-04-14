import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_240/data.json", "r") as f:
    data = json.load(f)

PreventionPillCost = data["PreventionPillCost"] # scalar parameter
TreatmentPillCost = data["TreatmentPillCost"] # scalar parameter
PreventionTreatmentRatio = data["PreventionTreatmentRatio"] # scalar parameter
MinTreatmentPills = data["MinTreatmentPills"] # scalar parameter
Budget = data["Budget"] # scalar parameter
NumberPreventionPills = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberPreventionPills")
NumberTreatmentPills = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberTreatmentPills")

# Add constraint to ensure NumberPreventionPills is at least PreventionTreatmentRatio times NumberTreatmentPills
model.addConstr(NumberPreventionPills >= PreventionTreatmentRatio * NumberTreatmentPills, name="prevention_treatment_ratio_constraint")

# Add constraint to ensure the number of treatment pills purchased meets the minimum requirement  
model.addConstr(NumberTreatmentPills >= MinTreatmentPills, name="min_treatment_pills_constraint")

# Add budget constraint for purchasing pills
model.addConstr(
    PreventionPillCost * NumberPreventionPills + TreatmentPillCost * NumberTreatmentPills <= Budget,
    name="budget_constraint"
)

# Non-negativity constraints for the number of pills
model.addConstr(NumberPreventionPills >= 0, name="non_negativity_prevention_pills")
model.addConstr(NumberTreatmentPills >= 0, name="non_negativity_treatment_pills")

# Add budget constraint
model.addConstr(
    NumberPreventionPills * PreventionPillCost + NumberTreatmentPills * TreatmentPillCost <= Budget,
    name="budget_constraint"
)

# Add minimum ratio constraint for prevention pills and treatment pills
model.addConstr(NumberPreventionPills >= PreventionTreatmentRatio * NumberTreatmentPills, name="min_ratio_prevention_treatment")

# Add constraint to ensure the minimum number of treatment pills purchased  
model.addConstr(NumberTreatmentPills >= MinTreatmentPills, name="min_treatment_pills_constraint")

# Set objective
model.setObjective(NumberTreatmentPills, gp.GRB.MAXIMIZE)

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
