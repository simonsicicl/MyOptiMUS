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
DosesOfMedicineA = model.addVar(vtype=gp.GRB.CONTINUOUS, name="DosesOfMedicineA")
DosesOfMedicineB = model.addVar(vtype=gp.GRB.CONTINUOUS, name="DosesOfMedicineB")

model.addConstr(DosesOfMedicineA >= 0, name="non_negativity_doses")

# Since DosesOfMedicineB is already defined as non-negative by default in Gurobi when the variable type is CONTINUOUS, no additional code is required.

# TotalMaterial constraint: Total imported material used for producing medicine A and B
model.addConstr(MaterialA * DosesOfMedicineA + MaterialB * DosesOfMedicineB <= TotalMaterial, name="total_material_constraint")

# Constraint: Total mRNA used for medicine A and B should not exceed the total available units of mRNA
model.addConstr(MrnaA * DosesOfMedicineA + MrnaB * DosesOfMedicineB <= TotalMrna, "total_mrna_usage")

# Add constraint for the maximum doses of medicine A
model.addConstr(DosesOfMedicineA <= MaxDosesA, name="max_doses_of_medicine_A")

model.addConstr(DosesOfMedicineA <= DosesOfMedicineB, 'DosesMedicineB_greater_DosesMedicineA')

model.addConstr(DosesOfMedicineA * MaterialA + DosesOfMedicineB * MaterialB <= TotalMaterial, name="material_usage")

# Constraint: The total units of mRNA used cannot exceed the total units available
model.addConstr(DosesOfMedicineA * MrnaA + DosesOfMedicineB * MrnaB <= TotalMrna, name="total_mRNA_usage")

# Add constraint for the maximum number of doses of medicine A
model.addConstr(DosesOfMedicineA <= MaxDosesA, name="max_doses_A")

# Set objective
model.setObjective(DosesOfMedicineA * PeopleA + DosesOfMedicineB * PeopleB, gp.GRB.MAXIMIZE)

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
