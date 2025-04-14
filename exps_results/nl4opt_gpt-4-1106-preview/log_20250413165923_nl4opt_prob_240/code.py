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
PreventionPills = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PreventionPills")
TreatmentPills = model.addVar(vtype=gp.GRB.INTEGER, name="TreatmentPills")

# Constraint: Number of prevention pills must be at least PreventionTreatmentRatio times the number of treatment pills
model.addConstr(PreventionPills >= PreventionTreatmentRatio * TreatmentPills, name="Prevention_Treatment_Ratio")

model.addConstr(TreatmentPills >= MinTreatmentPills, name="min_treatment_pills")

# Budget constraint for the total cost of purchasing prevention and treatment pills
model.addConstr(PreventionPillCost * PreventionPills + TreatmentPillCost * TreatmentPills <= Budget, name="budget_constraint")

# Add non-negativity constraints for the number of prevention and treatment pills
model.addConstr(PreventionPills >= 0, name="prevention_pills_nonnegativity")
model.addConstr(TreatmentPills >= 0, name="treatment_pills_nonnegativity")

# Ensure the total cost of prevention and treatment pills does not exceed the hospital's budget
model.addConstr(PreventionPillCost * PreventionPills + TreatmentPillCost * TreatmentPills <= Budget, name="budget_constraint")

# Ensure the number of prevention pills is at least twice the number of treatment pills
model.addConstr(PreventionPills >= PreventionTreatmentRatio * TreatmentPills, name="pill_ratio_constraint")

# Ensure the hospital purchases at least the minimum required number of treatment pills
model.addConstr(TreatmentPills >= MinTreatmentPills, name="min_treatment_pills")

# Set objective
model.setObjective(TreatmentPills, gp.GRB.MAXIMIZE)

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
