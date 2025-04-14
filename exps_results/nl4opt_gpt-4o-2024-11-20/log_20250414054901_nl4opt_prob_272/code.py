import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_272/data.json", "r") as f:
    data = json.load(f)

TimeMedicationPatches = data["TimeMedicationPatches"] # scalar parameter
MaterialsMedicationPatches = data["MaterialsMedicationPatches"] # scalar parameter
TimeAntiBioticCreams = data["TimeAntiBioticCreams"] # scalar parameter
MaterialsAntiBioticCreams = data["MaterialsAntiBioticCreams"] # scalar parameter
MaxTotalBatches = data["MaxTotalBatches"] # scalar parameter
TotalStaffTime = data["TotalStaffTime"] # scalar parameter
TotalMaterials = data["TotalMaterials"] # scalar parameter
PeopleTreatedMedicationPatches = data["PeopleTreatedMedicationPatches"] # scalar parameter
PeopleTreatedAntiBioticCreams = data["PeopleTreatedAntiBioticCreams"] # scalar parameter
MedicationPatches = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MedicationPatches")
AntibioticCreams = model.addVar(vtype=gp.GRB.CONTINUOUS, name="AntibioticCreams")

# No additional code required because the variable "MedicationPatches" is already non-negative due to its default lower bound (0) in Gurobi.

# Since the variable AntibioticCreams is defined with gp.GRB.CONTINUOUS, 
# it inherently satisfies the non-negativity constraint.

# Add constraint: The number of batches of anti-biotic creams must be at least twice the number of medication patches
model.addConstr(AntibioticCreams >= 2 * MedicationPatches, name="antibiotic_creams_minimum")

model.addConstr(MedicationPatches + AntibioticCreams <= MaxTotalBatches, name="total_batches_constraint")

# Add total staff time constraint
model.addConstr(
    MedicationPatches * TimeMedicationPatches + AntibioticCreams * TimeAntiBioticCreams <= TotalStaffTime,
    name="total_staff_time_constraint"
)

# Add material usage constraint
model.addConstr(
    MedicationPatches * MaterialsMedicationPatches + AntibioticCreams * MaterialsAntiBioticCreams <= TotalMaterials, 
    name="material_usage_constraint"
)

# Add constraint ensuring at least twice as many anti-biotic creams as medication patches
model.addConstr(AntibioticCreams >= 2 * MedicationPatches, name="antibioticcream_medpatch_ratio")

# Add constraint for total preparation time
model.addConstr(
    3 * MedicationPatches + 5 * AntibioticCreams <= TotalStaffTime, 
    name="total_preparation_time_constraint"
)

# Add materials usage constraint
model.addConstr(5 * MedicationPatches + 6 * AntibioticCreams <= TotalMaterials, name="materials_constraint")

# Add constraint: Total batches of medication patches and antibiotic creams cannot exceed maximum storage capacity
model.addConstr(MedicationPatches + AntibioticCreams <= MaxTotalBatches, name="max_storage_capacity")

# Add staff time constraint
model.addConstr(
    TimeMedicationPatches * MedicationPatches + TimeAntiBioticCreams * AntibioticCreams <= TotalStaffTime,
    name="staff_time_constraint"
)

# Add material usage constraint
model.addConstr(
    MedicationPatches * MaterialsMedicationPatches + AntibioticCreams * MaterialsAntiBioticCreams <= TotalMaterials,
    name="material_usage_constraint"
)

# Add production constraint to not exceed total number of batches
model.addConstr(MedicationPatches + AntibioticCreams <= MaxTotalBatches, name="production_constraint")

# Add proportional constraint to ensure at least twice as many anti-biotic creams as medication patches
model.addConstr(AntibioticCreams >= 2 * MedicationPatches, name="proportional_constraint")

# Set objective
model.setObjective(PeopleTreatedMedicationPatches * MedicationPatches + PeopleTreatedAntiBioticCreams * AntibioticCreams, gp.GRB.MAXIMIZE)

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
