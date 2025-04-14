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
NumberOfMedicationPatches = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfMedicationPatches")
NumberOfAntiBioticCreams = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfAntiBioticCreams")

# Since NumberOfMedicationPatches is already guaranteed to be non-negative by its variable type definition,
# no additional constraint is needed.
# The variable is an integer and Gurobi, by default, does not allow negative values for integer variables.

# Since the variable NumberOfAntiBioticCreams is already non-negative by its integer nature, no additional constraint is needed.

# Add constraint to ensure Anti-biotic creams are at least twice the number of medication patches
model.addConstr(NumberOfAntiBioticCreams >= 2 * NumberOfMedicationPatches, name="AntibioticCreams_to_Patches")



# Add staff time utilization constraint
model.addConstr(
    NumberOfMedicationPatches * TimeMedicationPatches +
    NumberOfAntiBioticCreams * TimeAntiBioticCreams <= 
    TotalStaffTime,
    name="staff_time_utilization"
)

# Add materials usage constraint
model.addConstr(MaterialsMedicationPatches * NumberOfMedicationPatches + MaterialsAntiBioticCreams * NumberOfAntiBioticCreams <= TotalMaterials, name="materials_usage")

# Add constraint to ensure the number of anti-biotic creams is at least twice the number of medication patches
model.addConstr(NumberOfAntiBioticCreams >= 2 * NumberOfMedicationPatches, 
                name="creams_at_least_twice_patches")

model.addConstr(NumberOfAntiBioticCreams >= 2 * NumberOfMedicationPatches, "antibiotic_cream_vs_med_patches")

# Define decision variables
NumberOfMedicationPatches = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfMedicationPatches")
NumberOfAntiBioticCreams = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfAntiBioticCreams")

# Define parameters
PeopleTreatedMedicationPatches = data["PeopleTreatedMedicationPatches"]  # scalar parameter
PeopleTreatedAntiBioticCreams = data["PeopleTreatedAntiBioticCreams"]  # scalar parameter

# Set objective function
model.setObjective(NumberOfMedicationPatches * PeopleTreatedMedicationPatches + NumberOfAntiBioticCreams * PeopleTreatedAntiBioticCreams, gp.GRB.MAXIMIZE)

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
