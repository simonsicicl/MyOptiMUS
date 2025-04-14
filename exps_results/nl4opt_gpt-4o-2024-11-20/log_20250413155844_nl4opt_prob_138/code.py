import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_138/data.json", "r") as f:
    data = json.load(f)

MaterialA = data["MaterialA"] # scalar parameter
MrnaA = data["MrnaA"] # scalar parameter
MaterialB = data["MaterialB"] # scalar parameter
MrnaB = data["MrnaB"] # scalar parameter
TotalMaterial = data["TotalMaterial"] # scalar parameter
TotalMrna = data["TotalMrna"] # scalar parameter
MaxDosesA = data["MaxDosesA"] # scalar parameter
PeopleA = data["PeopleA"] # scalar parameter
PeopleB = data["PeopleB"] # scalar parameter
DosesA = model.addVar(vtype=gp.GRB.CONTINUOUS, name="DosesA")
DosesB = model.addVar(vtype=gp.GRB.CONTINUOUS, name="DosesB")

# Non-negativity constraint for the number of doses of medicine A
model.addConstr(DosesA >= 0, name="non_negativity_DosesA")

# The variable DosesB is already defined as non-negative due to its default lower bound of 0 in Gurobi.

# Add constraint for total usage of imported material
model.addConstr(MaterialA * DosesA + MaterialB * DosesB <= TotalMaterial, name="material_usage_constraint")

# Add mRNA usage constraint
model.addConstr(DosesA * MrnaA + DosesB * MrnaB <= TotalMrna, name="mRNA_usage_constraint")

# Add constraint for maximum doses of medicine A
model.addConstr(DosesA <= MaxDosesA, name="max_doses_A")

# Add constraint: DosesB must be greater than DosesA by at least 1
model.addConstr(DosesB >= DosesA + 1, name="DosesB_greater_than_DosesA")

# Add imported material constraint
model.addConstr(MaterialA * DosesA + MaterialB * DosesB <= TotalMaterial, name="imported_material_constraint")

# Add mRNA availability constraint
model.addConstr(MrnaA * DosesA + MrnaB * DosesB <= TotalMrna, name="mRNA_availability")

# Add upper bound constraint on doses of medicine A
model.addConstr(DosesA <= MaxDosesA, name="upper_bound_dosesA")

# Non-negativity constraints for doses
model.addConstr(DosesA >= 0, name="nonneg_DosesA")
model.addConstr(DosesB >= 0, name="nonneg_DosesB")

# Set objective
model.setObjective(PeopleA * DosesA + PeopleB * DosesB, gp.GRB.MAXIMIZE)

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
